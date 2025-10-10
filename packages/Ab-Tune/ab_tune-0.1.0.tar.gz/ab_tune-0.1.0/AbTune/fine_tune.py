import os
import torch
import esm
from omegaconf import OmegaConf
from .esm_func import BatchConverter
from .models import ESM2TTT
from .base import TTTConfig

def update_cfg_func(cfg: TTTConfig, updates: dict = None) -> TTTConfig:
    """
    Update a TTTConfig dataclass using a dictionary of updates.
    Unknown keys in updates will be ignored safely.
    """
    if updates is None:
        return cfg

    # Convert updates to OmegaConf
    cfg_omegaconf = OmegaConf.create(updates)
    # Turn off struct mode temporarily to ignore unknown keys
    base_cfg = OmegaConf.structured(cfg)
    OmegaConf.set_struct(base_cfg, False)

    merged_cfg = OmegaConf.merge(base_cfg, cfg_omegaconf)
    # Convert back to dataclass
    updated_cfg = TTTConfig(**{
        k: v for k, v in OmegaConf.to_container(merged_cfg).items()
        if hasattr(cfg, k)  # ignore keys not in TTTConfig
    })
    return updated_cfg

def read_config(file_path: str) -> dict:
    cfg = OmegaConf.load(file_path)
    return OmegaConf.to_container(cfg, resolve=True)

def fine_tune_func(
    esm_model_name: str,
    seq: str, 
    pdbid_chainid: str,
    update_cfg: dict = None,
):
    """
    Fine-tune an ESM or ESMFold model using Test-Time Training (TTT).

    Args:
        esm_model_name: Name of pretrained ESM model (from esm.pretrained)
        input_seq: List containing tuples of (pdbid_chainid, sequence)
        update_cfg: Optional dictionary with TTT configuration updates
    """
    # -------------------------
    # Setup and validation
    # -------------------------
    input_seq = [(pdbid_chainid, seq)]  # Ensure input_seq is a list of tuples


    # Merge user config into default TTTConfig
    ttt_cfg = update_cfg_func(TTTConfig(), update_cfg)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # -------------------------
    # Load pretrained model
    # -------------------------
    mode = ttt_cfg.running_mode
    if mode in ["ESM2", "Conservation"]:
        try:
            model_func = getattr(esm.pretrained, esm_model_name)
            from .models import ESMFoldTTT  # Lazy import to avoid dependency if not needed
        except AttributeError:
            raise ValueError(f"Invalid model name '{esm_model_name}'. Must exist in esm.pretrained.")

        model, alphabet = model_func()
        model = model.to(device).eval()

        # -------------------------
        # Extract initial ESM representations
        # -------------------------
        seq_fix = [(None, input_seq)]  # BatchConverter expects [(label, seq)]
        _, _, batch_tokens = BatchConverter(alphabet)(seq_fix)
        batch_tokens = batch_tokens.to(device)
        batch_lens = (batch_tokens != alphabet.padding_idx).sum(1)
        try:
            layer_num = int(esm_model_name.split('_')[1][1:])  # e.g. esm2_t6_8M_UR50D -> 6
        except Exception:
            raise ValueError(f"Could not infer layer number from model name '{esm_model_name}'.")
        with torch.no_grad():
            results = model(batch_tokens, repr_layers=[layer_num])
        token_reps = results["representations"][layer_num][0, 1:batch_lens[0] - 1]
        if not os.path.exists(ttt_cfg.save_path):
            os.makedirs(ttt_cfg.save_path)
        torch.save(token_reps, f"{ttt_cfg.save_path}/{pdbid_chainid}_esm2.pt")

        # -------------------------
        # Handle running modes
        # -------------------------:
        model = ESM2TTT.ttt_from_pretrained(model, ttt_cfg)
        model.ttt(input_seq)

    elif mode == "ESMFold":
        # Load ESMFold
        try:
            fold_model = esm.pretrained.esmfold_v1()
        except Exception as e:
            raise RuntimeError(
                f"Failed to load ESMFold model: {e}. "
                "Ensure ESMFold and dependencies are correctly installed."
            )

        fold_model = fold_model.to(device).eval().float()

        # Save initial esmfold structure
        pdb = fold_model.infer_pdb(input_seq[0][1])
        with open(f"{ttt_cfg.save_path}/{pdbid_chainid}_esmfold.pdb", "w") as f:
            f.write(pdb)

        # Fine-tune via ESMFoldTTT
        fold_model = ESMFoldTTT.ttt_from_pretrained(
            fold_model, ttt_cfg=ttt_cfg, esmfold_config=fold_model.cfg
        )
        fold_model.ttt(input_seq)

    else:
        raise ValueError(f"Unknown running mode: '{ttt_cfg.running_mode}'")

    print(f"Finished fine-tuning in {ttt_cfg.running_mode} mode for {pdbid_chainid}.")