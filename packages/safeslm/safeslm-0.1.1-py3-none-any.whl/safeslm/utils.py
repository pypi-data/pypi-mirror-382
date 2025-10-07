import re
from typing import List, Optional

COMMON_TARGET_CANDIDATES = [
    "q_proj", "k_proj", "v_proj", "o_proj",  # many HF llama-like layers
    "c_attn", "c_proj",                      # gpt2-style: combined qkv in c_attn
    "qkv_proj", "qkv",                       # some libs use qkv concatenation
    "q_lin", "k_lin", "v_lin",
    "attn.q", "attn.k", "attn.v",
]

def infer_lora_target_modules(model, n_samples: int = 30) -> List[str]:
    """
    Inspect the model and return a list of substrings (module name pieces)
    that appear in the model parameters and are likely to be attention projections.

    Returns a non-empty list of candidate substrings or empty list if none matched.
    """
    sd_keys = list(getattr(model, "state_dict", lambda: {})().keys())
    # If state_dict empty, fallback to named_modules
    if not sd_keys:
        sd_keys = [name for name, _ in model.named_modules()]

    sd_text = " ".join(sd_keys[:n_samples*10])  # some heuristic chunk for speed

    found = []
    for cand in COMMON_TARGET_CANDIDATES:
        # look for whole-word-ish matches (dots/underscores allowed surrounding)
        if re.search(r"(^|[\._])" + re.escape(cand) + r"($|[\._])", sd_text):
            found.append(cand)

    # Deduplicate but keep order from COMMON_TARGET_CANDIDATES
    found = [f for f in COMMON_TARGET_CANDIDATES if f in found]

    return found

def debug_list_model_param_names(model, max_lines: int = 200):
    """
    Print a short sample of parameter/state_dict names to help debug which
    layer names your model actually uses.
    """
    try:
        keys = list(model.state_dict().keys())
    except Exception:
        keys = [name for name, _ in model.named_parameters()]
    print("[safeslm] Sample model parameter / state_dict keys (first {}):".format(min(max_lines, len(keys))))
    for k in keys[:max_lines]:
        print("  -", k)
