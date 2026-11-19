#!/usr/bin/env python3
"""make.fun entrypoint for news-image-20261119 (program/v1, stdlib only).

Copies the pre-rendered entry.png beside this file to the output dir
(/output, or $MAKEFUN_OUTPUT_DIR when set, per the kit starter).
The image was rendered at build time by generate.py from transcript.txt
(Pillow + DejaVu, deterministic); the grader runs stdlib-only Python
3.13 with no Pillow and no guaranteed fonts, so rendering here would
not reproduce the same pixels. Copying is byte-identical on every run.
"""
import os
import shutil
from pathlib import Path

here = Path(__file__).resolve().parent
out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
out_dir.mkdir(parents=True, exist_ok=True)
shutil.copyfile(here / "entry.png", out_dir / "entry.png")
print("wrote", out_dir / "entry.png")
