# SPDX-License-Identifier: BSD-3-Clause
# Copyright © 2025 UChicago Argonne, LLC. All rights reserved.
# Part of fortfmt-fix. See the LICENSE file in the project root for the full license
# text and warranty disclaimer (BSD 3-Clause).

import sys
import argparse
from pathlib import Path
from .core import transform_source

def main(argv=None):
    p = argparse.ArgumentParser(description="Rewrite DEC/Intel omitted-width FORMATs to standard-conforming forms.")
    p.add_argument("paths", nargs="+", help="Files or directories to process")
    p.add_argument("--dry-run", action="store_true", help="Print unified diff but do not write")
    p.add_argument("--in-place", action="store_true", help="Rewrite files in place")
    p.add_argument("--int64", action="store_true", help="Use wider integer defaults suitable for 64-bit I/O")
    p.add_argument("--listify-reads", action="store_true", help="Conservatively convert certain READs to list-directed form")
    p.add_argument("--trace", action="store_true", help="Verbose tracing")
    args = p.parse_args(argv)

    if not (args.dry_run ^ args.in_place):
        p.error("choose exactly one of --dry-run or --in-place")

    files = []
    for pth in map(Path, args.paths):
        if pth.is_dir():
            files += [*pth.rglob("*.f90"), *pth.rglob("*.F90"), *pth.rglob("*.f"), *pth.rglob("*.F")]
        else:
            files.append(pth)

    status = 0
    for f in files:
        try:
            src = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            src = f.read_text(encoding="latin-1")
        out = transform_source(src, int64=args.int64, listify_reads=args.listify_reads, trace=args.trace)
        if args.dry_run:
            if out != src:
                sys.stdout.write(f"# PATCH {f}\n")
                sys.stdout.write(_udiff(src, out, str(f)))
        else:
            if out != src:
                f.write_text(out, encoding="utf-8")
    return status

# simple inline diff without adding dependencies
import difflib

def _udiff(a, b, filename):
    return "".join(difflib.unified_diff(a.splitlines(True), b.splitlines(True),
                                        fromfile=filename, tofile=filename))

if __name__ == "__main__":
    raise SystemExit(main())
