# SPDX-License-Identifier: BSD-3-Clause
# Copyright © 2025 UChicago Argonne, LLC. All rights reserved.
# Part of fortfmt-fix. See the LICENSE file in the project root for the full license
# text and warranty disclaimer (BSD 3-Clause).

"""fortfmt-fix: Intel/DEC FORMAT codemod to standard-conforming Fortran I/O."""
from .core import transform_source, DEFAULTS
__all__ = ["transform_source", "DEFAULTS"]
