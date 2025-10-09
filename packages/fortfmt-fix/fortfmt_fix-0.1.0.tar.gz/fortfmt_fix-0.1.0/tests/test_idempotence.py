# SPDX-License-Identifier: BSD-3-Clause
# Copyright © 2025 UChicago Argonne, LLC. All rights reserved.
# Part of fortfmt-fix. See the LICENSE file in the project root for the full license
# text and warranty disclaimer (BSD 3-Clause).

from fortran_format_codemod import transform_source

def test_repeat_idempotence():
    src = """      program z
      write(*,'(3(I,1X),2(F.4))') 1,2,3,4.0,5.0
      end program
    """
    once = transform_source(src)
    twice = transform_source(once)
    # Should be idempotent - running transform twice should yield identical output
    assert once == twice
    # Also verify that the first transform actually changed something
    assert once != src
