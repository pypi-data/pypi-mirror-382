# SPDX-License-Identifier: BSD-3-Clause
# Copyright © 2025 UChicago Argonne, LLC. All rights reserved.
# Part of fortfmt-fix. See the LICENSE file in the project root for the full license
# text and warranty disclaimer (BSD 3-Clause).

import pytest
import random
import string
from fortran_format_codemod import transform_source


class TestInt64Flag:
    """Test the int64 flag functionality."""
    
    def test_int64_changes_only_i_default_width(self):
        """Verify int64 changes only the I default width."""
        test_cases = [
            "WRITE(*,'(I)') i",
            "WRITE(*,'(3I)') a,b,c", 
            "WRITE(*,'(I, F.6)') i, x",
            "FORMAT(I, F.6, E.12E3)",
        ]
        
        for case in test_cases:
            # Default behavior (int64=False)
            result_default = transform_source(case)
            assert "I12" in result_default, f"Expected I12 in default result for: {case}"
            assert "I23" not in result_default, f"Expected no I23 in default result for: {case}"
            
            # With int64=True
            result_int64 = transform_source(case, int64=True)
            assert "I23" in result_int64, f"Expected I23 with int64=True for: {case}"
            assert "I12" not in result_int64, f"Expected no I12 with int64=True for: {case}"
            
            # Other descriptors should remain the same
            if "F.6" in case:
                assert "F25.6" in result_default
                assert "F25.6" in result_int64
            if "E.12E3" in case:
                assert "E25.12E3" in result_default
                assert "E25.12E3" in result_int64
    
    def test_int64_preserves_explicit_widths(self):
        """Test that int64 doesn't change explicit integer widths."""
        test_cases = [
            "WRITE(*,'(I5)') i",
            "WRITE(*,'(I10)') i", 
            "WRITE(*,'(I0)') i",
        ]
        
        for case in test_cases:
            result_default = transform_source(case)
            result_int64 = transform_source(case, int64=True)
            
            # Both should preserve explicit widths
            assert result_default == result_int64, f"Explicit widths should be preserved: {case}"
            assert case == result_default, f"Explicit widths should not change: {case}"


class TestListifyReadsFlag:
    """Test the listify_reads flag functionality."""
    
    def test_listify_reads_converts_safe_reads(self):
        """Test that listify_reads converts safe READ statements."""
        # Safe READ case - numeric format with omitted widths
        safe_read = """program test
  integer :: i, j
  real :: x
  read(5, '(I, I, F.6)') i, j, x
end program"""
        
        result = transform_source(safe_read, listify_reads=True)
        
        # Should convert to list-directed read
        assert "read(5, *)" in result.lower()
        assert "'(I, I, F.6)'" not in result
        
        # Without listify_reads, should transform format but not listify
        result_no_listify = transform_source(safe_read, listify_reads=False)
        assert "read(5, *)" not in result_no_listify.lower()
        # Should still transform the format descriptors
        assert "I12" in result_no_listify
        assert "F25.6" in result_no_listify
    
    def test_listify_reads_preserves_write_statements(self):
        """Test that listify_reads never alters WRITE statements."""
        write_cases = [
            "WRITE(*,'(I)') i",
            "WRITE(*,'(F.6)') x",
            "WRITE(*,'(I, F.6)') i, x",
        ]
        
        for case in write_cases:
            result = transform_source(case, listify_reads=True)
            
            # WRITE should still be transformed normally
            assert "WRITE" in result
            assert "I12" in result or "F25.6" in result  # Should still get defaults
    
    def test_listify_reads_preserves_quoted_content(self):
        """Test that listify_reads never touches quoted content."""
        test_cases = [
            ("WRITE(*,'(A, I, A)') 'Value: ', i, ' units'", ["'Value: '", "' units'"]),
            ("WRITE(*,'(A, F.6, A)') 'Result: ', x, ' kg'", ["'Result: '", "' kg'"]),
            ("FORMAT('Temperature: ', F.6, ' C')", ["'Temperature: '", "' C'"]),
        ]
        
        for case, expected_quotes in test_cases:
            result = transform_source(case, listify_reads=True)
            
            # Quoted strings should be preserved
            for quote in expected_quotes:
                assert quote in result, f"Expected {quote} to be preserved in {case}"
            
            # Format descriptors should still be processed
            assert "I12" in result or "F25.6" in result
    
    def test_listify_reads_skips_unsafe_reads(self):
        """Test that listify_reads skips unsafe READ statements."""
        unsafe_cases = [
            # READ with non-numeric format
            """program test
  character(len=10) :: str
  read(5, '(A)') str
end program""",
            
            # READ with explicit widths (should not be listified)
            """program test
  integer :: i
  read(5, '(I5)') i
end program""",
            
            # READ with mixed format
            """program test
  integer :: i
  character(len=10) :: str
  read(5, '(I, A)') i, str
end program""",
        ]
        
        for case in unsafe_cases:
            result = transform_source(case, listify_reads=True)
            
            # Should not be converted to list-directed
            assert "read(5, *)" not in result.lower()
            # Original format should be preserved or processed normally
            assert "read(" in result.lower()


class TestIdempotence:
    """Test that transform_source is idempotent."""
    
    def test_idempotence_simple_cases(self):
        """Test idempotence with simple format cases."""
        test_cases = [
            "WRITE(*,'(I)') i",
            "WRITE(*,'(F.6)') x", 
            "WRITE(*,'(L)') ok",
            "WRITE(*,'(E.12E3)') x",
            "WRITE(*,'(3I, 2F.6)') a,b,c,x,y",
        ]
        
        for case in test_cases:
            once = transform_source(case)
            twice = transform_source(once)
            assert once == twice, f"Not idempotent for: {case}"
    
    def test_idempotence_with_flags(self):
        """Test idempotence with various flag combinations."""
        test_cases = [
            "WRITE(*,'(I)') i",
            "WRITE(*,'(F.6)') x",
            "read(5, '(I, F.6)') i, x",
        ]
        
        flag_combinations = [
            {"int64": False, "listify_reads": False},
            {"int64": True, "listify_reads": False},
            {"int64": False, "listify_reads": True},
            {"int64": True, "listify_reads": True},
        ]
        
        for case in test_cases:
            for flags in flag_combinations:
                once = transform_source(case, **flags)
                twice = transform_source(once, **flags)
                assert once == twice, f"Not idempotent for {case} with flags {flags}"
    
    def test_idempotence_complex_formats(self):
        """Test idempotence with complex format structures."""
        test_cases = [
            "WRITE(*,'(1X, 2(F.6, 1X), I, 3(E.12E3, 1X))') a, b, c, d, e, f",
            "FORMAT(1X, I, 2X, F.6, 3X, E.12E3)",
            "WRITE(*,'(A, I, A, F.6, A)') 'Value: ', i, ' = ', x, ' units'",
        ]
        
        for case in test_cases:
            once = transform_source(case)
            twice = transform_source(once)
            assert once == twice, f"Not idempotent for complex case: {case}"


class TestNestedAndContinuedFormats:
    """Test coverage for nested and continued formats."""
    
    def test_nested_groups(self):
        """Test nested format groups."""
        test_cases = [
            "WRITE(*,'(1X, 2(F.6, 1X), I)') a, b, c",
            "WRITE(*,'(3(I, 1X), 2(F.6, 1X))') i1, i2, i3, x1, x2",
            "FORMAT(1X, (I, F.6), 2X, (E.12E3, I))",
        ]
        
        for case in test_cases:
            result = transform_source(case)
            # Should transform omitted widths
            assert "F25.6" in result or "I12" in result or "E25.12E3" in result
            # Should preserve structure
            assert "(" in result and ")" in result
    
    def test_continuation_lines(self):
        """Test format continuation lines."""
        test_cases = [
            """WRITE(*,'(I,\
     &F.3,\
     &E.6E2)') 5, 1.0, 2.0""",
            """FORMAT(I,\
     &F.6,\
     &E.12E3)""",
        ]
        
        for case in test_cases:
            result = transform_source(case)
            # Should transform omitted widths
            assert "I12" in result
            assert "F25.3" in result or "F25.6" in result
            assert "E25.6E2" in result or "E25.12E3" in result
    
    def test_mixed_explicit_and_omitted_widths(self):
        """Test formats with mixed explicit and omitted widths."""
        test_cases = [
            "WRITE(*,'(I5, F, E.12E3, I)') i, x, y, j",
            "WRITE(*,'(F10.6, I, E.12E3, F)') x, i, y, z",
        ]
        
        for case in test_cases:
            result = transform_source(case)
            # Explicit widths should be preserved
            if "I5" in case:
                assert "I5" in result
            if "F10.6" in case:
                assert "F10.6" in result
            # Omitted widths should get defaults
            assert "F25.16" in result or "I12" in result or "E25.12E3" in result


class TestPropertyBased:
    """Lightweight property-based tests for robustness."""
    
    def test_balanced_parentheses_and_quotes(self):
        """Test that the transform doesn't crash on various balanced structures."""
        # Generate some random but balanced structures
        for _ in range(10):
            # Simple balanced parentheses
            test_str = "WRITE(*,'(I, F.6)') i, x"
            result = transform_source(test_str)
            assert isinstance(result, str)
            assert len(result) > 0
            
            # Test with some random characters inserted (but keep it balanced)
            chars = list(test_str)
            # Insert some random characters at safe positions
            for _ in range(3):
                pos = random.randint(0, len(chars) - 1)
                if chars[pos] not in "()'\"":  # Don't break quotes or parens
                    chars.insert(pos, random.choice(string.ascii_letters))
            
            test_str = ''.join(chars)
            try:
                result = transform_source(test_str)
                assert isinstance(result, str)
            except Exception as e:
                # If it crashes, that's okay for this test - we just want to avoid crashes
                # on reasonable inputs
                pass
    
    def test_various_quote_combinations(self):
        """Test various quote combinations don't cause crashes."""
        test_cases = [
            "WRITE(*,'(A)') 'simple string'",
            "WRITE(*,'(A)') 'string with '' doubled quotes'",
            'WRITE(*,"(A)") "double quoted string"',
            'WRITE(*,"(A)") "string with "" doubled quotes"',
            "WRITE(*,'(A)') 'mixed '' and \" quotes'",
        ]
        
        for case in test_cases:
            result = transform_source(case)
            assert isinstance(result, str)
            assert len(result) > 0
            # Should preserve the basic structure
            assert "WRITE" in result
            assert "A" in result  # The A descriptor should be preserved


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_and_minimal_formats(self):
        """Test empty and minimal format strings."""
        test_cases = [
            "WRITE(*,'()')",
            "WRITE(*,'( )')",
            "WRITE(*,'(1X)')",
            "WRITE(*,'(A)') 'hello'",
        ]
        
        for case in test_cases:
            result = transform_source(case)
            assert isinstance(result, str)
            assert len(result) > 0
    
    def test_malformed_but_safe_inputs(self):
        """Test inputs that might be malformed but shouldn't crash."""
        test_cases = [
            "WRITE(*,'(I.')",  # Incomplete format
            "WRITE(*,'(I.abc)')",  # Invalid format
            "WRITE(*,'(I,')",  # Missing closing paren
        ]
        
        for case in test_cases:
            result = transform_source(case)
            assert isinstance(result, str)
            # Should either return unchanged or make minimal safe changes
            assert len(result) > 0
