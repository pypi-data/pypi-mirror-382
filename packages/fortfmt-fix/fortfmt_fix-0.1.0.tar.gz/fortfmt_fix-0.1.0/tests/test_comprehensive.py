# SPDX-License-Identifier: BSD-3-Clause
# Copyright © 2025 UChicago Argonne, LLC. All rights reserved.
# Part of fortfmt-fix. See the LICENSE file in the project root for the full license
# text and warranty disclaimer (BSD 3-Clause).

import pytest
from fortran_format_codemod import transform_source

def test_bare_descriptors():
    """Test bare descriptors without any width or precision."""
    test_cases = [
        ("WRITE(*,'(F)') x", "WRITE(*,'(F25.16)') x"),
        ("WRITE(*,'(E)') x", "WRITE(*,'(E25.16E3)') x"),
        ("WRITE(*,'(D)') x", "WRITE(*,'(D25.16E3)') x"),
        ("WRITE(*,'(G)') x", "WRITE(*,'(G25.16)') x"),
        ("WRITE(*,'(ES)') x", "WRITE(*,'(ES25.16E3)') x"),
        ("WRITE(*,'(EN)') x", "WRITE(*,'(EN25.16E3)') x"),
    ]
    
    for before, expected in test_cases:
        result = transform_source(before)
        assert expected in result, f"Expected {expected} in result {result}"

def test_int64_flag():
    """Test that int64 flag changes integer default width."""
    src = "WRITE(*,'(I)') i"
    
    # Default behavior (int64=False)
    result_default = transform_source(src)
    assert "I12" in result_default
    
    # With int64=True
    result_int64 = transform_source(src, int64=True)
    assert "I23" in result_int64

def test_format_statements():
    """Test FORMAT statements (not just string literals)."""
    src = """program test
      integer :: i = 42
      real :: x = 3.14
      FORMAT(I, F.6)
      write(*, 100) i, x
100   FORMAT(I, F.6)
    end program"""
    
    result = transform_source(src)
    # Should transform both FORMAT statements
    assert "FORMAT(I12, F25.6)" in result
    assert result.count("FORMAT(I12, F25.6)") == 2

def test_quoted_strings_preserved():
    """Test that quoted strings inside formats are preserved."""
    src = """WRITE(*,'(A, I, A)') 'Value: ', i, ' units'"""
    result = transform_source(src)
    # Should only transform the I, not touch the quoted strings
    assert "I12" in result
    assert "'Value: '" in result
    assert "' units'" in result

def test_double_quoted_formats():
    """Test double-quoted format strings."""
    src = 'WRITE(*,"(I, F.6)") i, x'
    result = transform_source(src)
    assert "I12" in result
    assert "F25.6" in result

def test_repeat_counts():
    """Test repeat counts with omitted widths."""
    test_cases = [
        ("WRITE(*,'(3I)') a,b,c", "WRITE(*,'(3I12)') a,b,c"),
        ("WRITE(*,'(2F.6)') x,y", "WRITE(*,'(2F25.6)') x,y"),
        ("WRITE(*,'(5E.12E3)') arr", "WRITE(*,'(5E25.12E3)') arr"),
    ]
    
    for before, expected in test_cases:
        result = transform_source(before)
        assert expected in result

def test_mixed_formats():
    """Test formats with mixed explicit and omitted widths."""
    src = "WRITE(*,'(I5, F, E.12E3, I)') i, x, y, j"
    result = transform_source(src)
    # Should only transform the omitted widths (F -> F25.16, I -> I12)
    assert "I5" in result  # explicit width preserved
    assert "F25.16" in result  # omitted width filled
    assert "E25.12E3" in result  # omitted width filled
    assert "I12" in result  # omitted width filled

def test_listify_reads():
    """Test the listify_reads functionality."""
    src = """program test
      integer :: i, j
      real :: x
      read(5, '(I, I, F.6)') i, j, x
    end program"""
    
    result = transform_source(src, listify_reads=True)
    # Should convert to list-directed read
    assert "read(5, *)" in result.lower()
    assert "'(I, I, F.6)'" not in result

def test_listify_reads_preserves_write():
    """Test that listify_reads doesn't affect WRITE statements."""
    src = """program test
      integer :: i = 42
      write(*, '(I)') i
    end program"""
    
    result = transform_source(src, listify_reads=True)
    # WRITE should still be transformed normally
    assert "write(*, '(i12)')" in result.lower()

def test_complex_nested_formats():
    """Test complex nested format structures."""
    src = """WRITE(*,'(1X, 2(F.6, 1X), I, 3(E.12E3, 1X))') a, b, c, d, e, f"""
    result = transform_source(src)
    # Should transform all omitted widths
    assert "F25.6" in result
    assert "I12" in result
    assert "E25.12E3" in result

def test_trace_flag():
    """Test that trace flag doesn't break functionality."""
    src = "WRITE(*,'(I)') i"
    result = transform_source(src, trace=True)
    # Should still work with trace enabled
    assert "I12" in result
    assert isinstance(result, str)
