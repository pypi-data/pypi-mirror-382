import copy
import time
import typing as T
from omegaconf import OmegaConf
from pathlib import Path
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Union
from pathlib import Path

import pandas as pd
import torch
from .lora import inject_trainable_lora
from .utils import setup_logger, preserve_model_state, get_optimal_window

from Bio.PDB import PDBParser
from io import StringIO
import numpy as np


#code adapted from https://github.com/anton-bushuiev/ProteinTTT

@dataclass
class TTTConfig:

    """
    Configuration for test-time training (TTT).
    """
    
    lr: float = 4e-4
    ags: int = 1
    steps: int = 30
    lora_rank: int = 4
    lora_alpha: float = 32.0
    lora_target_replace_module: str = 'MultiheadAttention' #lora replace module
    momentum: float = 0.0
    weight_decay: float = 0.0
    batch_size: int = 2
    mask_ratio: float = 0.15  # Used for ESM2 / ESMFold, SaProt, ProSST pre-training
    crop_size: int = 1024  # Used for ESM2 / ESMFold, SaProt, ProSST pre-training
    bert_leave_prob: float = 0.1 
    bert_replace_prob: float = 0.1
    score_seq_steps_list: T.Any = None  # T.Optional[int | list[int]]. 
    eval_each_step: bool = True
    initial_state_reset: bool = True
    seed: T.Optional[int] = 0  # None means using environment seed
    log_file_path: T.Optional[str] = None
    log_name: str = 'ttt_log'
    debug: bool = False
    inject_layers: list[int] = field(default_factory=lambda: [0]) # Which layers to inject LoRA into
    save_path: T.Optional[str] = None # Path to save outout from ttt; either csv or .pt or .pdb or all of them 
    layer_num_inference: int = 0
    running_mode : str = 'ESMFold' #3 options ['ESMFold', 'conservation', 'ESM2']
    #either 'ESMFold' (output plexciity, embedding, CDR plddt if provided f and save pdb file) ; or conservation study with input is wt_seq and mut_seq, fine-tune on wt and then calcaulte the logits for wt and mut at each step; 


    @classmethod
    def from_yaml(cls, yaml_path: Union[str, Path]) -> 'TTTConfig':
        """Load TTTConfig from a YAML file using OmegaConf."""
        default_conf = OmegaConf.structured(cls)
        file_conf = OmegaConf.load(yaml_path)
        conf = OmegaConf.merge(default_conf, file_conf)
        OmegaConf.resolve(conf)
        return cls(**OmegaConf.to_container(conf))
    
class TTTModule(torch.nn.Module, ABC):
    ttt_default_cfg: T.Optional[TTTConfig] = None

    def __init__(
        self,
        ttt_cfg: T.Optional[TTTConfig] = None,
    ):
        ABC.__init__(self)  # no torch.nn.Module init because it is already done in child class 

        # Init TTTConfig
        self.ttt_cfg = ttt_cfg or TTTConfig()
        if isinstance(ttt_cfg, Path) or isinstance(ttt_cfg, str):
            self.ttt_cfg = TTTConfig.from_yaml(ttt_cfg)

        # Set random seed if specified, otherwise use environment seed
        self.ttt_generator = torch.Generator()
        if self.ttt_cfg.seed is not None:
            self.ttt_generator.manual_seed(self.ttt_cfg.seed)

        # Init logger
        self.ttt_logger = setup_logger(
            log_file_path=self.ttt_cfg.log_file_path, 
            log_name=self.ttt_cfg.log_name,
            debug=self.ttt_cfg.debug
        )
        self.ttt_logger.debug(f"TTTConfig: {self.ttt_cfg}")

        # Store initial state of trainable modules
        self._ttt_initial_state = None
        if self.ttt_cfg.initial_state_reset:
            self._ttt_initial_state = self._ttt_get_state()

    @classmethod
    def ttt_from_pretrained(
        cls, 
        model: torch.nn.Module,
        ttt_cfg: T.Optional[TTTConfig] = None,
        **kwargs
    ) -> 'TTTModule':
        # Use default TTTConfig if not provided
        if ttt_cfg is None:
            ttt_cfg = cls.ttt_default_cfg or TTTConfig()

        # Initialize instance without pretrained state
        instance = cls(ttt_cfg, **kwargs)

        # Copy state from pretrained model
        for key, value in model.__dict__.items():
            setattr(instance, key, value)

        # Store initial state of trainable modules after initializing weights
        if instance.ttt_cfg.initial_state_reset:
            instance._ttt_initial_state = instance._ttt_get_state()

        return instance


    @preserve_model_state
    def ttt(
        self,
        seq: T.Optional[str] = None,
        **kwargs
    ) -> None:
        """
        Run TTT loop. After calling this method, the model will be customized to the input protein
        via test-time training (TTT).

        Args:
            seq: Input amino acid sequence to customize the model to.
            **kwargs: Keyword arguments to forward of the original model

        Returns:
            A dictionary containing the results of the TTT loop.
        """

        # Tokenize input sequence
        batch_labels, x = self._ttt_tokenize(seq, **kwargs)  
        
        # Get trainable parameters and optimizer
        parameters = self._ttt_get_parameters()

        optimizer = self._ttt_get_optimizer(parameters)
        optimizer.zero_grad()

        # Initialize dictionaries to store results and metrics each TTT step
        df = []
        ttt_step_data = defaultdict(dict)


        # Run TTT loop
        x = x.to(next(self.parameters()).device)
        loss = None
        self.eval()
        for step in range(self.ttt_cfg.steps + 1):
            # Sample batch
            batch_masked, targets, mask, start_indices = self._ttt_sample_batch(x)  # [bs, seq_len]

            #log every ags steps
                # Measure time since the beginning of the last TTT step
            if step == 0:
                last_step_time = time.time()
            ttt_step_time = time.time() - last_step_time

            # Score sequence
            _, perplexity = None, None
            should_score = (
                    self.ttt_cfg.score_seq_steps_list is not None)

            if should_score and step in self.ttt_cfg.score_seq_steps_list:
                score_seq_start_time = time.time()
                score_func = self._ttt_score_seq
                perplexity = score_func(x, batch_labels, **kwargs)
            else:
                perplexity = None

            ttt_step_data[step]['perplexity'] = perplexity

            # Store all metrics in a row
            result_dict = {}
            row = dict(
                step=step,
                loss=loss.item() if loss is not None else None,
                perplexity=perplexity,
                ttt_step_time=ttt_step_time,
            )
            df.append(row)

            # Log
            log_row = ', '.join([
                f'{k}: {v:.5f}' if isinstance(v, float) else
                f'{k}: {", ".join([f"{subk}: {subv:.5f}" if isinstance(subv, float) else f"{subk}: None" if subv is None else f"{subk}: {subv}" for subk, subv in v.items()])}' if isinstance(v, dict) else
                f'{k}: None' if v is None else
                f'{k}: {v}'
                for k, v in row.items()
            ])

            self.ttt_logger.info(log_row)

            last_step_time = time.time()

            # Last step is just for logging
            if step == self.ttt_cfg.steps * self.ttt_cfg.ags:
                break


            # Forward pass
            self.train()
            logits = self._ttt_predict_logits(batch_masked, start_indices, **kwargs)

            # Calculate loss
            loss = self._ttt_cross_entropy_loss(logits, targets, mask)

            # Backward pass
            loss.backward()
            if (step + 1) % self.ttt_cfg.ags == 0:
                optimizer.step()
                optimizer.zero_grad()
            self.eval()  

            if self.ttt_cfg.running_mode == 'ESM2':
                self._calculate_embeddings(
                    x=x,
                    batch_labels=batch_labels,
                    save_path=self.ttt_cfg.save_path,
                    layer_num=self.ttt_cfg.layer_num_inference,
                    step_number=step // self.ttt_cfg.ags,
                    **kwargs
                )
            

            elif self.ttt_cfg.running_mode == 'Conservation':
                self._calculate_conservation_logits(
                    logits=logits,
                    batch_labels=batch_labels,
                    step=step // self.ttt_cfg.ags
                )

            elif self.ttt_cfg.running_mode == 'ESMFold':
                self._save_pdb(
                    seq=seq[0][1],
                    batch_labels=batch_labels,
                    step=step // self.ttt_cfg.ags,
                    save_path=self.ttt_cfg.save_path,
                    **kwargs
                )

                


        #save the weight of the best state
        #save_path = os.path.join(self.ttt_cfg.embedding_save_path, f"step_{best_step}.pt")
        #torch.save(best_state, save_path)

        df = pd.DataFrame(df)



    def ttt_reset(self) -> None:
        if self._ttt_initial_state is None:
            raise ValueError("Initial state is not set. Make sure initial_state_reset=True in TTTConfig.")
        self._ttt_set_state(self._ttt_initial_state)
    

    @abstractmethod
    def _ttt_tokenize(self, seq: T.Optional[str] = None, **kwargs) -> torch.Tensor:
        raise NotImplementedError("Subclass must implement _ttt_tokenize method")

    @abstractmethod
    def _ttt_predict_logits(self, batch: torch.Tensor, start_indices: torch.Tensor = None) -> torch.Tensor:
        """
        Predict logits for a batch of sequences.

        Args:
            batch: Batch of sequences to predict logits for.
            start_indices: Starting indices of sequences in the batch with respect to the 
                original input sequence used for TTT customization. This argument may be needed
                as a result of cropping.
        """
        raise NotImplementedError("Subclass must implement _ttt_predict_logits method")
    
    @abstractmethod
    def _ttt_mask_token(self, token: int) -> int:
        raise NotImplementedError("Subclass must implement _ttt_mask_token method")
    
    @abstractmethod
    def _ttt_get_non_special_tokens(self) -> torch.Tensor:
        raise NotImplementedError("Subclass must implement _ttt_get_non_special_tokens method")

    @abstractmethod
    def _ttt_get_padding_token(self) -> int:
        raise NotImplementedError("Subclass must implement _ttt_get_padding_token method")

    @abstractmethod
    def _ttt_token_to_str(self, token: int) -> str:
        raise NotImplementedError("Subclass must implement _ttt_token_to_str method")

    def _ttt_get_trainable_modules(self) -> list[torch.nn.Module]:
        """
        Return a list of modules to train. _ttt_get_frozen_modules is called after this function, so
        the returned modules can contain parameters that will be frozen.
        """
        return [self]
    

    def _ttt_get_parameters(self) -> T.Iterator[torch.nn.Parameter]:
        """
        Configures and returns trainable parameters for TTT.

        If lora_rank > 0, injects LoRA layers into modules within 
        _ttt_get_trainable_modules() and makes only LoRA parameters trainable. Otherwise, 
        makes parameters trainable in _ttt_get_trainable_modules() excluding _ttt_get_frozen_modules().

        Returns:
            Iterator of parameters requiring gradients
        """
        # Freeze all parameters
        for param in self.parameters():
            param.requires_grad = False

        # Get modules to train
        module_list = self._ttt_get_trainable_modules()


        # Unfreeze parameters to train
        if self.ttt_cfg.lora_rank > 0:  # Train only LoRA parameters
            require_grad_param_groups = []
            for module in module_list:
                require_grad_params, names = inject_trainable_lora(
                    module,
                    target_replace_module=self.ttt_cfg.lora_target_replace_module,
                    r=self.ttt_cfg.lora_rank,
                    scale=self.ttt_cfg.lora_alpha,
                    inject_layers=self.ttt_cfg.inject_layers,
                    verbose=False,
                )
                require_grad_param_groups.append(require_grad_params)
            for param_groups in require_grad_param_groups:
                for param_group in param_groups:
                    for param in param_group:
                        param.requires_grad = True
        else:  # Train all specified parameters
            for module in module_list:
                for param in module.parameters():
                    param.requires_grad = True


        #self.ttt_logger.info("Parameters to be trained during TTT:")
        num_trainable_params = 0
        for name, p in self.named_parameters():
            if p.requires_grad:
                self.ttt_logger.debug(f"{name} {p.shape}")
                num_trainable_params += p.numel()
        
        #total number of trainable parameters 
        return filter(lambda p: p.requires_grad, self.parameters())

    def _ttt_get_optimizer(self, parameters: T.Iterator[torch.nn.Parameter]) -> torch.optim.Optimizer:

        optimizer = torch.optim.SGD(
            parameters, 
            lr=self.ttt_cfg.lr, 
            momentum=self.ttt_cfg.momentum, 
            weight_decay=self.ttt_cfg.weight_decay
        )

        return optimizer


    def _ttt_get_state(self) -> T.Any:
        """Creates a deep copy of all child modules' states.

        The whole modules rather than parameters are saved to avoid support changing modules such
        as in the case of LoRA.

        Returns:
            A dictionary mapping module names to their copied states.
        """
        state = {}
        for name, module in self.named_children():
            state[name] = copy.deepcopy(module)
        return state

    def _ttt_set_state(self, state: T.Any) -> None:
        """Restores model to a previously saved state.

        Args:
            state: Dictionary of module states from _ttt_get_state()
        """
        for k, v in state.items():
            if hasattr(self, k):
                delattr(self, k)
            self.add_module(k, copy.deepcopy(v))

    def _ttt_sample_batch(
        self,
        x: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        _, seq_len = x.shape
        batch_size = self.ttt_cfg.batch_size
        crop_size = self.ttt_cfg.crop_size

        # Create batch of unmasked and uncropped sequences
        if x.shape[0] == 1:
            # If only one sequence, replicate it batch_size times
            x_expanded = x.expand(batch_size, -1)

        # Sample crop_size-tokens cropped subsequences
        if seq_len < crop_size:
            start_indices = torch.zeros(batch_size, dtype=torch.long)
            crop_size = seq_len
        else:
            start_indices = torch.randint(0, seq_len - crop_size + 1, (batch_size,), generator=self.ttt_generator).to(torch.long)
        batch_cropped = torch.stack([x_expanded[i, start:start + crop_size] for i, start in enumerate(start_indices)])

        # Get non-special tokens
        non_special_tokens = self._ttt_get_non_special_tokens()
        non_special_tokens_set = set(non_special_tokens)
        # Apply BERT masking only to non-special tokens
        mask = torch.zeros((batch_size, crop_size), dtype=torch.bool)
        for i in range(batch_size):
            non_special_positions = [j for j in range(crop_size) if batch_cropped[i,j].item() in non_special_tokens_set]
            if len(non_special_positions) > 0:
                num_to_mask = int(len(non_special_positions) * self.ttt_cfg.mask_ratio)
                if num_to_mask > 0:
                    positions_to_mask = torch.tensor(non_special_positions)[torch.randperm(len(non_special_positions), generator=self.ttt_generator)[:num_to_mask]]
                    mask[i, positions_to_mask] = True

        batch_masked = batch_cropped.clone()
        for i in range(batch_size):
            for idx in torch.nonzero(mask[i], as_tuple=True)[0]:
                if self.ttt_cfg.bert_leave_prob + self.ttt_cfg.bert_replace_prob > 0:
                    prob = torch.rand(1, generator=self.ttt_generator).item()
                    if prob < 1 - self.ttt_cfg.bert_leave_prob - self.ttt_cfg.bert_replace_prob:  # 80% random chance to mask token
                        batch_masked[i, idx] = self._ttt_mask_token(batch_masked[i, idx])
                    elif prob < 1 - self.ttt_cfg.bert_leave_prob:  # 10% chance to change to random token
                        batch_masked[i, idx] = non_special_tokens[torch.randint(0, len(non_special_tokens), (1,), generator=self.ttt_generator).item()]
                    else:  # 10% chance to keep current token
                        pass
                else:
                    # 100% change to mask token
                    batch_masked[i, idx] = self._ttt_mask_token(batch_masked[i, idx])

        # Targets are the original cropped sequences
        targets = batch_cropped

        return batch_masked, targets, mask, start_indices

    def _ttt_cross_entropy_loss(
        self,
        logits: torch.Tensor,
        targets: torch.Tensor,
        mask: torch.Tensor
    ) -> torch.Tensor:
        assert logits.ndim == 3, "Logits must be a 3D tensor [bs, seq_len, vocab_size]"
        bs, seq_len, vocab_size = logits.shape

        # Flatten logits and targets
        logits_reshaped = logits.view(-1, vocab_size)  # [bs*seq_len, vocab_size]
        targets_reshaped = targets.view(-1)  # [bs*seq_len]
        mask_reshaped = mask.view(-1).bool()  # [bs*seq_len]

        # Calculate cross-entropy loss over masked tokens
        loss = torch.nn.functional.cross_entropy(
            logits_reshaped[mask_reshaped],
            targets_reshaped[mask_reshaped],
            reduction='none'
        )  # [bs*seq_len]

        # Split loss back into per-sequence chunks and average each sequence separately
        masked_tokens_per_seq = mask.sum(dim=1)  # [bs]
        loss_split = torch.split(loss, masked_tokens_per_seq.tolist())  # List of [n_masked] tensors
        seq_losses = torch.stack([chunk.mean() for chunk in loss_split])  # [bs]
        loss = seq_losses.mean()
        return loss
    

    def _ttt_score_seq(self, x: torch.Tensor, batch_labels: torch.Tensor = None, **kwargs) -> tuple[list[torch.Tensor], float]:
        """
        Score a sequence using TTT. 

        If the sequence is a multiple sequence alignment (MSA), only the first sequence is 
        used for scoring. The function handles special tokens by skipping them for perplexity
        calculation and putting zeros for log-probabilities. The function also handles the case
        when the sequence length is larger than the model context size (crop_size) by using the
        optimal window selection from ProteinGym when masking tokens.

        Returns:
            all_log_probs: Log probabilities for each token in the sequence when masked.
            perplexity: Perplexity of the sequence.
        """
        # Check input shape
        assert x.ndim == 2, "Input must be a 2D tensor"
        assert x.shape[0] == 1, "Input batch size must be 1"
    
        _, perplexity = self._ttt_score_seq_pseudo_perplexity(x, **kwargs)
        return perplexity


    def _ttt_score_seq_pseudo_perplexity(
        self,
        x: torch.Tensor,
        **kwargs
    ) -> tuple[list[torch.Tensor], float]:
        # Get model-specific token sets
        all_tokens = self._ttt_get_all_tokens()
        non_special_tokens = self._ttt_get_non_special_tokens()

        all_log_probs = []  # [seq_len, vocab_size]
        wt_log_probs = []  # [seq_len]. Only for non-special tokens to calculate perplexity

        for i in range(x.size(-1)):

            # Check if the token is a special token
            i_special = False
            token = x[0, i]
            if token not in non_special_tokens:
                i_special = True

            # Mask current token
            x_masked = x.clone().to(x.device)
            x_masked[0, i] = self._ttt_mask_token(x_masked[0, i])
            
            # If sequence length is larger than the model context size, use the optimal window selection
            if x.size(-1) > self.ttt_cfg.crop_size:
                start, end = get_optimal_window(
                    mutation_position_relative=i,
                    seq_len_wo_special=x.size(-1),  # len(args.sequence)+2 in ProteinGym
                    model_window=self.ttt_cfg.crop_size
                )
                x_masked = x_masked[..., start:end]
            else:
                start=0

            # Predict logs for each token (amino acid) at the position
            with torch.no_grad():
                start_indices = torch.tensor([start], device=x.device)
                logits = self._ttt_predict_logits(x_masked, start_indices, **kwargs)
                token_log_probs = torch.log_softmax(logits, dim=-1)
                all_log_probs.append(token_log_probs[:, i-start])  # [1, vocab size]

            # Skip appending wild-type log-probabilities for special tokens (used later for perplexity calculation)
            if not i_special:
                wt_log_probs.append(token_log_probs[0, i-start, x[0, i-start]].item())

        # Stack log probabilities into a single tensor [seq_len, vocab_size]
        all_log_probs = torch.cat(all_log_probs, dim=0)

        # Calculate perplexity from wild-type log-probabilities
        perplexity = torch.exp(-torch.mean(torch.tensor(wt_log_probs))).item()

        return all_log_probs, perplexity


    def _get_sequence_index(self, x: torch.Tensor, seq_label: str, infor_file: str)  -> int:
        """
        Get the start and end index of CDR regions for antibodies from a csv file.
        Args:
            x: Input tensor containing the sequence label in the format [pdbid_chainid].
            seq_label: A string residue number which CDR region to get the indices for (e.g., 'CDRH3').
            infor_file: Path to the CSV file containing CDR indices: formated as 
            pdbid, CDRH1, CDRH2, CDRH3, CDRL1, CDRL2, CDRL3
            6zjg,25-32,52-56,98-108,23-33,49-55,88-98
        """
        name = x[0]
        pdbid = name.split('_')[0]
        chainid = name.split('_')[1]
        df = pd.read_csv(infor_file, sep=',')
        #get the index from the tabel
        if '-' in seq_label:
            seq_label = seq_label.split('-')[-1]
        index = df[(df['pdbid'] == pdbid)][seq_label].values[0]
        start_resiude, end_residue = int(index.split('-')[0]), int(index.split('-')[1])
        return start_resiude, end_residue


    def _calculate_conservation_logits(self, logits, batch_labels: T.Optional[torch.Tensor] = None, step: int = 0):
        alphabet = self.ttt_alphabet

        probs = torch.nn.functional.softmax(logits, dim=-1)  

        aa_tokens = alphabet.all_toks  
        aa_tokens = [tok for tok in aa_tokens if len(tok) == 1 and tok.isalpha()]  # e.g., ['A', 'C', ..., 'Y']
        # Slice probabilities to those AA indices (if known)
        aa_indices = [alphabet.get_idx(tok) for tok in aa_tokens]
        probs = probs[..., aa_indices] 

        # ---- Convert to DataFrame ----
        dfs = []
        for batch_idx in range(probs.shape[0]):
            seq_df = pd.DataFrame(
                probs[batch_idx].detach().cpu().numpy(),
                columns=aa_tokens
            )
            seq_df['position'] = range(1, probs.shape[1] + 1)
            seq_df = seq_df[['position'] + aa_tokens]
            seq_df['batch'] = batch_idx
            dfs.append(seq_df)

        df_all = pd.concat(dfs, ignore_index=True)
        df_all.to_csv(f"{self.ttt_cfg.save_path}/{batch_labels[0]}_step{step}_logits.csv", index=False)


    def _ttt_score_sequence_recovery_score(
        self,
        x: torch.Tensor,
        batch_labels: T.Optional[torch.Tensor] = None,  #name of the input sequqence [pdbid_chainid]
        seq_label: T.Optional[str] = None,  #name of the loop to be masked [CDRH3]
        **kwargs
    ) -> tuple[list[torch.Tensor], float]:
        """
        Score a sequence by masking 15% of residues within a user-defined range of residue indices.

        Args:
            x: Input sequence tensor of shape [1, seq_len].
            mask_range: A tuple specifying the range of residue indices (start, end) to consider for masking.
            **kwargs: Additional arguments for model-specific scoring.

        Returns:
            all_log_probs: Log probabilities for each token in the sequence when masked.
            recovery_score: The sequence recovery score, calculated as the proportion of correctly predicted residues.
        """
        # Validate input
        assert x.ndim == 2 and x.shape[0] == 1, "Input must be a 2D tensor with batch size 1"
        # Get model-specific token sets
        all_tokens = self._ttt_get_all_tokens()
        non_special_tokens = self._ttt_get_non_special_tokens()

        start_idx, end_idx = self._get_sequence_index(batch_labels, seq_label)
        if start_idx is not None or end_idx is not None:
            assert 0 <= start_idx < end_idx <= x.size(1), "Invalid mask range"

            all_log_probs = []  # [seq_len, vocab_size]
            correct_predictions = 0
            total_masked = 0

            # Mask 15% of residues within the specified range
            num_positions_to_mask = max(1, int((end_idx - start_idx) * 0.15))
            positions_to_mask = torch.randperm(end_idx - start_idx, generator=self.ttt_generator)[:num_positions_to_mask] + start_idx

            for pos in positions_to_mask:
                # Mask current token
                x_masked = x.clone().to(x.device)
                x_masked[0, pos] = self._ttt_mask_token(x_masked[0, pos])

                # Predict log probabilities for the masked sequence
                with torch.no_grad():
                    logits = self._ttt_predict_logits(x_masked, torch.tensor([0], device=x.device), **kwargs)
                    token_log_probs = torch.log_softmax(logits, dim=-1)
                    all_log_probs.append(token_log_probs[:, pos])  # [1, vocab_size]

                    # Check if the model correctly predicts the original token
                    predicted_token = torch.argmax(token_log_probs[0, pos]).item()
                    if predicted_token == x[0, pos].item():
                        correct_predictions += 1

                total_masked += 1

            # Stack log probabilities into a single tensor [seq_len, vocab_size]
            all_log_probs = torch.cat(all_log_probs, dim=0)

            # Calculate sequence recovery score
            recovery_score = correct_predictions / total_masked if total_masked > 0 else 0.0
        else:
            all_log_probs = None
            recovery_score = None

        return all_log_probs, recovery_score
    

    def _ttt_eval_step(self, x: torch.Tensor, batch_labels: T.Optional[torch.Tensor], step: int, score_selction_kind: str, **kwargs) -> float:

        _, recovery_score = self._ttt_score_sequence_recovery_score(
            x=x,
            batch_labels=batch_labels,
            seq_label=score_selction_kind,
            **kwargs
        )

        return recovery_score

    def _save_pdb(self, seq: str, batch_labels: T.Optional[torch.Tensor], step: int, save_path: str):
 
        """
        Save the predicted structure in PDB format and calculate local pLDDT for a specific chain and residue range.
        Args:
            seq (str): Input amino acid sequence.
            batch_labels (torch.Tensor): Tensor containing the label of the input sequence, formatted as [pdbid_chainid].
            score_selction_kind (str): A string indicating which part of the sequence to evaluate, formatted as 'something-sequence_label'.
        """

        #seq_label = score_selction_kind.split('-')[-1]  # Extract the sequence label from the score selection kind
        
        #start_idx, end_idx = self._get_sequence_index(batch_labels, score_selction_kind)

        with torch.no_grad():
            pdb_str = self.infer_pdb(seq, masking_pattern=None)

        save_pdb_name = f"{save_path}/{batch_labels[0]}_step{step}.pdb"
        with open(save_pdb_name, 'w') as f:
            f.write(pdb_str)

        plddt = self._local_plddt(pdb_str, chain_id=batch_labels[0].split('_')[1])
        # Store predictions
        eval_step_preds = {'pdb': pdb_str}
        eval_step_metric_dict = {'plddt': plddt}
        confidence = plddt

        return eval_step_preds, eval_step_metric_dict, confidence



    def _local_plddt(
        self, 
        pdb_str: str, 
        chain_id: str, 
        start_residue: int = None, 
        end_residue: int = None
    ) -> float:
        """
        Local pLDDT calculation for a specific chain and residue range.
        """
        parser = PDBParser(QUIET=True)
        structure = parser.get_structure('model', StringIO(pdb_str))
        
        plddt_scores = []

        for model in structure:
            if chain_id not in model:
                raise ValueError(f"Chain ID '{chain_id}' not found in model.")
            chain = model[chain_id]

            for residue in chain:
                res_id = residue.get_id()[1]  # residue number
                if (start_residue is None or res_id >= start_residue) and \
                (end_residue is None or res_id <= end_residue):
                    for atom in residue:
                        plddt_scores.append(atom.get_bfactor())

        if not plddt_scores:
            raise ValueError(
                f"No pLDDT scores found for chain {chain_id} "
                f"in range {start_residue}-{end_residue}"
            )

        avg_plddt = float(np.mean(plddt_scores))
        return avg_plddt


    def _calculate_embeddings(
        self, 
        x: torch.Tensor,
        batch_labels: T.Optional[torch.Tensor],  #name of the input sequqence [pdbid_chainid]
        save_path: str, 
        layer_num: int,
        step_number: int
    ) -> None:
        """
        Calculate embeddings using the best fine-tuned state of the model.
        Args:
            input_seq (List[Tuple[str, str]]): List of input sequences [(name, sequence)].
            save_path (str): Path to save the embeddings.
            layer_num (int): Layer number from which to extract representations. Defaults to the last layer (-1).
        """
        # Restore the best state
        # Ensure the model is in evaluation mode

        self.eval()

        # Perform forward pass to get token representations
        with torch.no_grad():
            results = self(x, repr_layers=[layer_num])  # Forward pass
            token_representations = results["representations"][layer_num]

        # Extract and save sequence-level representations
        for i, _ in enumerate(x):
            labels = batch_labels[i]
            batch_lens = x[i].shape[0]
            seq_repr = token_representations[i, 1 : batch_lens - 1]  # Exclude special tokens
            seq_avg_repr = seq_repr.mean(dim=1)
            torch.save(seq_avg_repr, f"{save_path}/{labels}_step{step_number}.pt")  # Save to file


