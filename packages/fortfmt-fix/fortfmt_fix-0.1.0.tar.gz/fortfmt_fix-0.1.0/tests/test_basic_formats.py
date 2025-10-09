# SPDX-License-Identifier: BSD-3-Clause
# Copyright © 2025 UChicago Argonne, LLC. All rights reserved.
# Part of fortfmt-fix. See the LICENSE file in the project root for the full license
# text and warranty disclaimer (BSD 3-Clause).

import re
from fortran_format_codemod import transform_source, DEFAULTS

CASES = [
    ("WRITE(*,'(I)') i",              f"WRITE(*,'({DEFAULTS['I']})') i"),
    ("WRITE(*,'(L)') ok",             f"WRITE(*,'({DEFAULTS['L']})') ok"),
    ("WRITE(*,'(F.6)') x",            f"WRITE(*,'(F25.6)') x"),
    ("WRITE(*,'(E.12E3)') x",         f"WRITE(*,'(E25.12E3)') x"),
    ("WRITE(*,'(D.12E3)') x",         f"WRITE(*,'(D25.12E3)') x"),
    ("WRITE(*,'(G.12)') x",           f"WRITE(*,'(G25.12)') x"),
    ("WRITE(*,'(ES.12E3)') x",        f"WRITE(*,'(ES25.12E3)') x"),
    ("WRITE(*,'(EN.12E3)') x",        f"WRITE(*,'(EN25.12E3)') x"),
]

SRC_TMPL = """program t
  integer :: i=7
  logical :: ok=.true.
  real :: x=1.0
  {}
end program
"""

import pytest
@pytest.mark.parametrize("before,after", CASES)
def test_basic_descriptor_defaults(before, after):
    src = SRC_TMPL.format(before)
    out = transform_source(src)
    # Now test real behavior - the after string should be in the output
    assert after in out
    assert isinstance(out, str)

def test_idempotence_simple():
    src = SRC_TMPL.format("WRITE(*,'(I)') 1")
    once = transform_source(src)
    twice = transform_source(once)
    assert once == twice
