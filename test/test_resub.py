import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import os
import pytest
import tempfile
from unittest.mock import patch
from resub import replace, parse_args, process_files

@pytest.fixture
def temp_file():
    # Fixture to create a temporary file for testing
    temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w+')
    temp_file.write("Line 1: foo\nLine 2: bar\nLine 3: baz\n")
    temp_file.close()
    yield temp_file.name
    # Cleanup after test
    os.remove(temp_file.name)

def test_replace_basic(temp_file):
    # Pass required arguments: pattern and replacement
    opts = parse_args(['foo', 'replaced'])
    replaced = replace(temp_file, 'foo', 'replaced', opts)
    
    # Verify that replacement was made
    with open(temp_file, 'r') as f:
        content = f.read()
    assert replaced
    assert "replaced" in content
    assert "foo" not in content

def test_replace_no_match(temp_file):
    # Pass required arguments: pattern and replacement
    opts = parse_args(['nonexistent', 'replaced'])
    replaced = replace(temp_file, 'nonexistent', 'replaced', opts)
    
    # Verify that no replacement was made
    with open(temp_file, 'r') as f:
        content = f.read()
    assert not replaced
    assert "replaced" not in content
    assert "foo" in content

def test_replace_with_dry_run(temp_file):
    # Pass required arguments: pattern and replacement, along with the --dry-run flag
    opts = parse_args(['foo', 'replaced', '--dry-run'])
    replaced = replace(temp_file, 'foo', 'replaced', opts)
    
    # Verify that the file was not modified
    with open(temp_file, 'r') as f:
        content = f.read()
    assert replaced
    assert "foo" in content  # Original content should remain

def test_replace_with_confirm(temp_file):
    # Pass required arguments: pattern and replacement, along with the --confirm flag
    opts = parse_args(['foo', 'replaced', '--confirm'])
    
    # Mock the user input to simulate confirmation
    with patch('builtins.input', return_value='y'):
        replaced = replace(temp_file, 'foo', 'replaced', opts)
    
    # Verify that the replacement was made after confirmation
    with open(temp_file, 'r') as f:
        content = f.read()
    assert replaced
    assert "replaced" in content
    assert "foo" not in content

def test_replace_with_match_pattern(temp_file):
    # Pass required arguments: pattern and replacement, along with the --match flag
    opts = parse_args(['foo', 'replaced', '--match', 'Line 1'])
    replaced = replace(temp_file, 'foo', 'replaced', opts)
    
    # Verify that the replacement was only made for the matching line
    with open(temp_file, 'r') as f:
        content = f.read()
    assert replaced
    assert "replaced" in content
    assert "foo" not in content
    assert "bar" in content  # No modification in other lines

def test_replace_with_nomatch_pattern(temp_file):
    # Pass required arguments: pattern and replacement, along with the --nomatch flag
    opts = parse_args(['foo', 'replaced', '--nomatch', 'Line 2'])
    replaced = replace(temp_file, 'foo', 'replaced', opts)
    
    # Verify that the replacement skipped the lines matching the nomatch pattern
    with open(temp_file, 'r') as f:
        content = f.read()
    assert replaced
    assert "replaced" in content
    assert "foo" not in content
    assert "bar" in content  # No modification on Line 2

@pytest.fixture
def temp_dir_with_files():
    # Fixture to create a temporary directory with multiple files for testing recursive behavior
    temp_dir = tempfile.TemporaryDirectory()
    files = []
    for i in range(3):
        temp_file = os.path.join(temp_dir.name, f"testfile_{i}.txt")
        with open(temp_file, 'w') as f:
            f.write(f"Test content foo in file {i}\n")
        files.append(temp_file)
    yield temp_dir.name, files
    temp_dir.cleanup()

def test_process_files_recursive(temp_dir_with_files):
    # Test processing files recursively in a directory
    temp_dir, files = temp_dir_with_files
    opts = parse_args(['foo', 'replaced', '--recursive'])

    process_files([temp_dir], opts, 'foo', 'replaced')
    
    # Verify that the replacement was applied to all files in the directory
    for file in files:
        with open(file, 'r') as f:
            content = f.read()
        assert "replaced" in content
        assert "foo" not in content

def test_replace_symlink():
    # Create a temp file and a symlink pointing to it
    target_file = tempfile.NamedTemporaryFile(delete=False, mode='w+')
    target_file.write("Symlink target content foo\n")
    target_file.close()

    symlink_path = target_file.name + "_symlink"
    os.symlink(target_file.name, symlink_path)

    opts = parse_args(['foo', 'replaced'])

    # Perform replacement on the symlink
    replaced = replace(symlink_path, 'foo', 'replaced', opts)

    # Check the symlink target's content was modified, not the symlink itself
    with open(target_file.name, 'r') as f:
        content = f.read()

    assert replaced
    assert "replaced" in content
    assert "foo" not in content

    # Ensure the symlink still exists and points to the correct target
    assert os.path.islink(symlink_path)
    assert os.readlink(symlink_path) == target_file.name

    # Cleanup
    os.remove(symlink_path)
    os.remove(target_file.name)

def test_replace_preserves_permissions(temp_file):
    # Get the original file permissions
    original_permissions = os.stat(temp_file).st_mode

    opts = parse_args(['foo', 'replaced'])
    replace(temp_file, 'foo', 'replaced', opts)

    # Check the permissions are still the same
    assert os.stat(temp_file).st_mode == original_permissions
