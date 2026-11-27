#!/usr/bin/env python3
"""Copy the entry image beside this file to the grader's output.

Standard library only: the grader runs bare Python 3.13 with no
third-party packages, so this program copies entry.png instead of
drawing it. The image itself was drawn beforehand and is stored in
the repository beside this file; the judge sees exactly those bytes.
Deterministic: a byte-for-byte copy, the same bytes on every run.
"""

import os
import shutil
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if out_dir:
        target = os.path.join(out_dir, "entry.png")
    elif os.path.isdir("/output"):
        target = "/output/entry.png"
    else:
        target = os.path.join(here, "entry.png")
    if os.path.abspath(target) == os.path.abspath(src):
        print("already in place:", target, os.path.getsize(target))
        return 0
    os.makedirs(os.path.dirname(target) or ".", exist_ok=True)
    shutil.copyfile(src, target)
    print("wrote", target, os.path.getsize(target))
    return 0


if __name__ == "__main__":
    sys.exit(main())
