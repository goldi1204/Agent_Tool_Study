import json
import random
import re
from typing import List, Dict, Optional

try:
    from datasets import load_dataset
    HAS_DATASETS = True
except ImportError:
    HAS_DATASETS = False

def _make_distractor_from_answer(answer: str, seed: int = 42) -> str:
    rnd = random.Random(seed + abs(hash(answer)) % 1000000)
    a = answer.strip()
    
    try:
        num = float(a)
        if num.is_integer():
            num = int(num)
            delta = rnd.choice([1, 2, 3, -1, -2, -3, 10, -10])
            ds = num + delta
            if ds == num:
                ds += 1
            return str(ds)
        else:
            delta = rnd.uniform(0.1, 5.0)
            ds = num + delta
            if ds == num:
                ds += 1.0
            return str(round(ds, 2))
    except (ValueError, AttributeError):
        if len(a) <= 6:
            return a + "_x"
        return a.split()[0] + " (incorrect)"

def _extract_final_answer(answer_str: str) -> str:
    """GSM8K answers often contain reasoning. Extract final numeric answer."""
    m = re.findall(r"[-+]?\d*\.?\d+", answer_str)
    return m[-1] if m else answer_str.strip()

def load_local_json(path: str, max_examples: Optional[int] = None) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if max_examples:
        data = data[:max_examples]
    
    out = []
    for i, ex in enumerate(data):
        _id = ex.get("id", f"json_{i}")
        text = ex.get("text") or ex.get("question") or ex.get("prompt")
        gt = ex.get("ground_truth") or ex.get("answer") or ex.get("label")
        ds = ex.get("distractor") or _make_distractor_from_answer(str(gt), seed=42 + i)
        out.append({"id": _id, "text": text, "ground_truth": gt, "distractor": ds})
    return out

def load_huggingface_dataset(hf_spec: str, split: str = "train", max_examples: Optional[int] = None, extract_numeric: bool = True) -> List[Dict]:
    if not HAS_DATASETS:
        raise RuntimeError("Please install the `datasets` package (pip install datasets) to load HuggingFace datasets.")
    
    parts = hf_spec.split(":", 1)
    name = parts[0]
    config = parts[1] if len(parts) == 2 else None
    
    ds = load_dataset(name, config) if config else load_dataset(name)
    
    if split not in ds:
        dataset_split = ds["train"]
    else:
        dataset_split = ds[split]
    
    results = []
    for idx, row in enumerate(dataset_split):
        if max_examples and idx >= max_examples:
            break
        
        text = row.get("question") or row.get("problem") or row.get("prompt") or row.get("text")
        gt = row.get("answer") or row.get("label") or row.get("target")
        
        if isinstance(gt, str):
            gt = gt.strip()
            if extract_numeric and name.lower() in ["gsm8k", "math"]:
                gt = _extract_final_answer(gt)
        else:
            gt = str(gt)
        
        distractor = _make_distractor_from_answer(str(gt), seed=1000 + idx)
        
        rec_id = f"hf:{name}:{split}:{idx}"
        results.append({"id": rec_id, "text": text, "ground_truth": gt, "distractor": distractor})
    
    return results

def load_dataset_generic(source: str, max_examples: Optional[int] = None, hf_split: str = "train") -> List[Dict]:
    if source.startswith("json:"):
        path = source.split("json:", 1)[1]
        return load_local_json(path, max_examples=max_examples)
    
    if source.startswith("hf:"):
        spec = source.split("hf:", 1)[1]
        parts = spec.split(":")
        name = parts[0]
        split = parts[1] if len(parts) > 1 else hf_split
        return load_huggingface_dataset(name, split=split, max_examples=max_examples)
    
    raise ValueError(f"Unknown source prefix. Use json: or hf:. Got {source}")

def validate_dataset_schema(dataset: List[Dict]) -> None:
    required = {"id", "text", "ground_truth", "distractor"}
    for i, ex in enumerate(dataset):
        if not required.issubset(set(ex.keys())):
            missing = required - set(ex.keys())
            raise ValueError(f"Example index {i} missing fields: {missing}")
        if ex["text"] is None or str(ex["text"]).strip() == "":
            raise ValueError(f"Example index {i} has empty text")
        if ex["ground_truth"] is None:
            raise ValueError(f"Example index {i} has no ground_truth")
