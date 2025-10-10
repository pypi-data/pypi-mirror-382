# run_AbTune.py
import argparse
from .fine_tune import fine_tune_func, read_config

def main(config_path=None):
    """
    Entry point for Ab-Tune CLI.
    If config_path is None, reads from command line args.
    """
    if config_path is None:
        parser = argparse.ArgumentParser(description="Run ESM Fine-tuning with AbTune")
        parser.add_argument("--config", type=str, required=True, help="Path to YAML config file")
        args = parser.parse_args()
        config_path = args.config

    updates = read_config(config_path)
    esm_model_name = updates["esm_model_name"]
    seq = updates["seq"]
    pdbid_chainid = updates["pdbid_chainid"]

    fine_tune_func(esm_model_name, seq, pdbid_chainid, update_cfg=updates)

# Optional: allow running with python -m ab_tune.run_AbTune
if __name__ == "__main__":
    main()
