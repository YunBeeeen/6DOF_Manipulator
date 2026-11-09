#!/usr/bin/env python3
"""Run the geometric label generator used for Stage4 training labels."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "ml"))
from labeling.relation import resolve_relation


def main():
    scene = {
        "red_block": {"x": 0.10, "y": 0.00},
        "blue_block": {"x": 0.30, "y": 0.10},
        "green_block": {"x": 0.25, "y": -0.10},
        "basket": {"x": 0.40, "y": 0.00},
    }
    result = {
        "leftmost": resolve_relation(scene, [{"relation": "leftmost", "reference": None}]),
        "nearest_to(basket)": resolve_relation(scene, [{"relation": "nearest_to", "reference": "basket"}]),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
