# SPDX-License-Identifier: BSD-3-Clause
# Copyright © 2025 UChicago Argonne, LLC. All rights reserved.
# Part of fortfmt-fix. See the LICENSE file in the project root for the full license
# text and warranty disclaimer (BSD 3-Clause).

from fortran_format_codemod import transform_source

def test_nested_parens_and_repeats():
    src = """      program x
      real :: a,b
      write(*,'(1X,2(F.6,1X),I)') a,b,5
      end program
    """
    out = transform_source(src)
    # Should transform the F.6 to F25.6 and I to I12
    assert "F25.6" in out
    assert "I12" in out
    assert isinstance(out, str)

def test_continuation_lines():
    src = """      program y
      write(*,'(I,\
     &F.3,\
     &E.6E2)') 5, 1.0, 2.0
      end program
    """
    out = transform_source(src)
    # Should transform I to I12, F.3 to F25.3, E.6E2 to E25.6E2
    assert "I12" in out
    assert "F25.3" in out
    assert "E25.6E2" in out
    assert isinstance(out, str)
