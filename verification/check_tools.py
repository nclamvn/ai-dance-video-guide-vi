#!/usr/bin/env python3
"""Kiểm các chốt dừng có ý nghĩa; không gọi dịch vụ, không tạo media."""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / (name + ".py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    sync = module("sync_music")
    budget = module("budget")
    rng = np.random.default_rng(2086)
    original = rng.normal(size=sync.RATE * 10)
    padding = round(.35 * sync.RATE)
    music = np.r_[rng.normal(size=padding), original, rng.normal(size=sync.RATE)]
    offset, confident, _ = sync.estimate_offset(music, original, 10)
    assert confident and abs(offset - .35) <= 1 / sync.RATE
    unrelated = rng.normal(size=sync.RATE * 12)
    assert not sync.estimate_offset(unrelated, original, 10)[1]
    repeated = np.r_[original, np.zeros(sync.RATE), original]
    assert not sync.estimate_offset(repeated, original, 10)[1]
    stretched = np.interp(np.arange(len(original) * 1.01) / 1.01,
                          np.arange(len(original)), original)
    assert not sync.estimate_offset(stretched, original, 10)[1]
    empty = budget.calculate(json.loads((ROOT / "templates/budget.json").read_text()))
    assert empty["status"] == "INCOMPLETE" and empty["within_cap"] is None
    data = {"cap_credits": 100, "reserve_credits": 5,
            "items": [{"id": "trial", "quantity": 1, "unit_credits": 60, "attempts": 2}]}
    over = budget.calculate(data)
    assert over["within_cap"] is False and over["total_credits"] == "125"
    data["items"][0]["attempts"] = 1
    assert budget.calculate(data)["within_cap"] is True
    print(json.dumps({"status": "PASS", "checks": [
        "known_waveform_offset", "unrelated_music_rejected", "repeated_ambiguous_music_rejected",
        "tempo_drift_rejected", "missing_quotes_incomplete", "over_cap_rejected", "within_cap_arithmetic"
    ], "scope": "Synthetic deterministic gate checks, not visual quality or service certification",
        "numpy_version": np.__version__}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
