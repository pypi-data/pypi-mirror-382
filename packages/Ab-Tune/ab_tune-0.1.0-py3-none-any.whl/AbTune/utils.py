from functools import wraps
import torch
import logging
import sys


#code re-factored from https://github.com/anton-bushuiev/ProteinTTT

def setup_logger(log_file_path=None, log_name='log', debug=False):
    """Setup a logger with a file handler and a stream handler.
    
    Copy from https://github.com/pluskal-lab/DreaMS/blob/4fbc05e6b264961e47906bafe6cd5f495a8cea54/dreams/utils/io.py#L38
    
    Args:
        log_file_path (str, optional): Path to the log file.
        log_name (str, optional): Name of the logger.
        debug (bool, optional): Whether to set the logger to debug level.
    """
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.INFO if not debug else logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

    if logger.hasHandlers():
        logger.handlers.clear()

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    if log_file_path:
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def preserve_model_state(func):
    """A decorator that preserves a model's training state, gradient computation settings, and device.

    This decorator saves and restores:
    1. The model's training mode (train/eval)
    2. The requires_grad state of all model parameters
    3. The device (CPU/GPU) of the model and its parameters

    It ensures the model returns to its original state after the decorated function
    completes, even if an exception occurs during execution.

    Args:
        func: The function to be decorated, typically a method of a PyTorch model.

    Returns:
        The wrapped function that preserves the model state.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # Store original training state
        was_training = self.training

        # Store original requires_grad states
        orig_requires_grad = {name: param.requires_grad for name, param in self.named_parameters()}

        # Store original device
        orig_device = next(self.parameters()).device

        try:
            # Run the function
            result = func(self, *args, **kwargs)
            return result
        finally:
            # Restore original training state
            self.train(was_training)

            # Restore original requires_grad states
            for name, param in self.named_parameters():
                if name in orig_requires_grad:
                    param.requires_grad = orig_requires_grad[name]
                else:
                    param.requires_grad = False

            # Restore original device
            self.to(orig_device)

    return wrapper


def get_optimal_window(mutation_position_relative, seq_len_wo_special, model_window):
    """Helper function that selects an optimal sequence window that fits the maximum model context 
    size. If the sequence length is less than the maximum context size, the full sequence is
    returned.

    Copied from https://github.com/anton-bushuiev/ProteinGym/blob/a4866852c6fc8844993fca9416946a7fdc27aa7c/proteingym/baselines/trancepteve/trancepteve/utils/scoring_utils.py#L60
    """
    half_model_window = model_window // 2
    if seq_len_wo_special <= model_window:
        return [0,seq_len_wo_special]
    elif mutation_position_relative < half_model_window:
        return [0,model_window]
    elif mutation_position_relative >= seq_len_wo_special - half_model_window:
        return [seq_len_wo_special - model_window, seq_len_wo_special]
    else:
        return [
            max(0,mutation_position_relative-half_model_window),
            min(seq_len_wo_special,mutation_position_relative+half_model_window)
        ]

