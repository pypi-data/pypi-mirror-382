# SPDX-License-Identifier: BSD-3-Clause
# Copyright © 2025 UChicago Argonne, LLC. All rights reserved.
# Part of fortfmt-fix. See the LICENSE file in the project root for the full license
# text and warranty disclaimer (BSD 3-Clause).

import pytest
import subprocess
import tempfile
import shutil
import os
from pathlib import Path


def test_cli_smoke():
    """Test that the CLI works correctly with dry-run and in-place editing."""
    
    # Get the path to the sample file
    sample_path = Path(__file__).parent / "samples" / "sample.f90"
    assert sample_path.exists(), f"Sample file not found: {sample_path}"
    
    # Create a temporary copy for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.f90', delete=False) as tmp_file:
        # Copy the sample content
        shutil.copy2(sample_path, tmp_file.name)
        tmp_path = tmp_file.name
    
    try:
        # Test 1: Dry-run should produce a diff containing expanded descriptors
        result = subprocess.run(
            ["fortfmt-fix", "--dry-run", tmp_path],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Check that the output contains expected transformations
        output = result.stdout
        assert "I12" in output, "Expected I12 in dry-run output"
        assert "L2" in output, "Expected L2 in dry-run output"
        assert "F25.6" in output, "Expected F25.6 in dry-run output"
        assert "I12" in output, "Expected I12 in dry-run output"
        
        # Test 2: In-place edit should modify the file
        result = subprocess.run(
            ["fortfmt-fix", "--in-place", tmp_path],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Check that the file was modified
        with open(tmp_path, 'r') as f:
            modified_content = f.read()
        
        assert "I12" in modified_content, "Expected I12 in modified file"
        assert "L2" in modified_content, "Expected L2 in modified file"
        assert "F25.6" in modified_content, "Expected F25.6 in modified file"
        
        # Test 3: Second dry-run should show no changes (idempotence)
        result = subprocess.run(
            ["fortfmt-fix", "--dry-run", tmp_path],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Check that no changes are needed
        output = result.stdout
        assert "PATCH" not in output, "Expected no PATCH in second dry-run (idempotence)"
        
    finally:
        # Clean up
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_cli_int64_flag():
    """Test that the --int64 flag works correctly."""
    
    # Get the path to the sample file
    sample_path = Path(__file__).parent / "samples" / "sample.f90"
    
    # Create a temporary copy for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.f90', delete=False) as tmp_file:
        # Copy the sample content
        shutil.copy2(sample_path, tmp_file.name)
        tmp_path = tmp_file.name
    
    try:
        # Test with --int64 flag
        result = subprocess.run(
            ["fortfmt-fix", "--int64", "--dry-run", tmp_path],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Check that the output uses I23 instead of I12
        output = result.stdout
        assert "I23" in output, "Expected I23 with --int64 flag"
        assert "I12" not in output, "Expected no I12 with --int64 flag"
        
    finally:
        # Clean up
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def test_cli_help():
    """Test that the CLI help works."""
    
    result = subprocess.run(
        ["fortfmt-fix", "--help"],
        capture_output=True,
        text=True,
        check=True
    )
    
    # Check that help output contains expected information
    output = result.stdout
    assert "usage:" in output.lower(), "Expected usage information in help"
    assert "paths" in output, "Expected paths argument in help"
    assert "--dry-run" in output, "Expected --dry-run option in help"
    assert "--in-place" in output, "Expected --in-place option in help"
    assert "--int64" in output, "Expected --int64 option in help"
