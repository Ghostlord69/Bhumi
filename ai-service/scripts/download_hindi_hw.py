#!/usr/bin/env python3
"""Download IIIT-INDIC-HW-WORDS-Hindi (handwritten Devanagari words) for OCR fine-tuning.

Examples:
  python scripts/download_hindi_hw.py --out ../samples/handwritten/hindi/words_full --limit 2000
  python scripts/download_hindi_hw.py --out ../samples/handwritten/hindi/words_full --limit 0
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Download Hindi handwritten word OCR data")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("../samples/handwritten/hindi/words_full"),
        help="Output directory",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=2000,
        help="Max train samples (0 = entire train split)",
    )
    parser.add_argument(
        "--dataset",
        default="c3rl/IIIT-INDIC-HW-WORDS-Hindi",
        help="Hugging Face dataset id",
    )
    args = parser.parse_args()

    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise SystemExit("Install first: pip install datasets pillow") from exc

    out: Path = args.out
    images_dir = out / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading {args.dataset} (train)…")
    ds = load_dataset(args.dataset, split="train")
    n = len(ds) if args.limit <= 0 else min(args.limit, len(ds))

    labels_path = out / "labels.tsv"
    with labels_path.open("w", encoding="utf-8") as f:
        f.write("image\ttext\n")
        for i in range(n):
            row = ds[i]
            text = row["text"]
            img = row["image"]
            name = f"word_{i:06d}.jpg"
            img.convert("RGB").save(images_dir / name, quality=95)
            f.write(f"{name}\t{text}\n")
            if (i + 1) % 500 == 0:
                print(f"  saved {i + 1}/{n}")

    info = {
        "name": "IIIT-INDIC-HW-WORDS-Hindi",
        "language": "हिन्दी",
        "huggingface": args.dataset,
        "original": "https://ilocr.iiit.ac.in/dataset/18/",
        "saved": n,
        "labels": str(labels_path),
    }
    (out / "dataset_info.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Done: {n} word images → {out}")


if __name__ == "__main__":
    main()
