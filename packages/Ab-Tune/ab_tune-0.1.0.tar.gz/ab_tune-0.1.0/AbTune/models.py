import typing as T

import torch
from esm.model.esm2 import ESM2

from . import esm_func
from .base import TTTModule, TTTConfig

#code re-factored from https://github.com/anton-bushuiev/ProteinTTT

class ESM2TTT(TTTModule, ESM2):

    def __init__(self, ttt_cfg: TTTConfig, **kwargs):
        ESM2.__init__(self, **kwargs)
        TTTModule.__init__(self, ttt_cfg=ttt_cfg)
        self.ttt_alphabet = esm_func.Alphabet.from_architecture("ESM-1b")  # ESM2 uses ESM-1b alphabet
        self.ttt_batch_converter = self.ttt_alphabet.get_batch_converter()

    def _ttt_tokenize(self, seq: str, **kwargs):
        batch_labels, batch_strs, batch_tokens = self.ttt_batch_converter([(None, seq)])
        return batch_labels, batch_tokens

    def _ttt_get_frozen_modules(self) -> list[torch.nn.Module]:
        return [self.embed_tokens]
    
    def _ttt_mask_token(self, token: int) -> int:
        return self.ttt_alphabet.mask_idx
    
    def _ttt_get_padding_token(self) -> int:
        return self.ttt_alphabet.padding_idx

    def _ttt_token_to_str(self, token: int) -> str:
        return self.ttt_alphabet.all_toks[token]

    def _ttt_get_all_tokens(self) -> list[int]:
        return [self.ttt_alphabet.tok_to_idx[t] for t in self.ttt_alphabet.all_toks]
    
    def _ttt_get_non_special_tokens(self) -> list[int]:
        return [self.ttt_alphabet.tok_to_idx[t] for t in self.ttt_alphabet.standard_toks]

    def _ttt_predict_logits(self, batch: torch.Tensor, start_indices: torch.Tensor = None, **kwargs) -> torch.Tensor:
        return self(batch)["logits"]  # [bs, seq_len] -> [bs, seq_len, vocab_size]




class ESMFoldTTT(TTTModule):
    def __init__(self, ttt_cfg: TTTConfig, **kwargs):
        try:
            from esm.esmfold.v1.esmfold import ESMFold
        except ImportError:
            raise ImportError(
                "ESMFoldTTT requires the optional package 'esmfold'. "
                "Install it with `pip install ab-tune[esmfold]`."
            )

        # Initialize parent classes
        ESMFold.__init__(self, **kwargs)
        TTTModule.__init__(self, ttt_cfg=ttt_cfg)
        self.ttt_alphabet = esm_func.Alphabet.from_architecture("ESM-1b")
        self.ttt_batch_converter = self.ttt_alphabet.get_batch_converter()


    def _ttt_tokenize(self, seq: str, **kwargs) -> torch.Tensor:
        batch_labels, batch_strs, batch_tokens = self.ttt_batch_converter([(None, seq)])
        return batch_labels, batch_tokens


    def _ttt_get_trainable_modules(self) -> list[torch.nn.Module]:
        return [self.esm]

    def _ttt_get_frozen_modules(self) -> list[torch.nn.Module]:
        return [self.esm.embed_tokens]
    
    def _ttt_mask_token(self, token: int) -> int:
        return self.ttt_alphabet.mask_idx
    
    def _ttt_get_padding_token(self) -> int:
        return self.ttt_alphabet.padding_idx

    def _ttt_token_to_str(self, token: int) -> str:
        return self.ttt_alphabet.all_toks[token]

    def _ttt_get_all_tokens(self) -> list[int]:
        return [self.ttt_alphabet.tok_to_idx[t] for t in self.ttt_alphabet.all_toks]
    
    def _ttt_get_non_special_tokens(self) -> list[int]:
        return [self.ttt_alphabet.tok_to_idx[t] for t in self.ttt_alphabet.standard_toks]

    def _ttt_predict_logits(self, batch: torch.Tensor, start_indices: torch.Tensor = None, **kwargs) -> torch.Tensor:
        return self.esm(batch)["logits"]  # [bs, seq_len] -> [bs, seq_len, vocab_size]