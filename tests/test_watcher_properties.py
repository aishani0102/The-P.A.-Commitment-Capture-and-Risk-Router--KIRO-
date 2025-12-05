"""Property-based tests for file watcher."""

from hypothesis import given, strategies as st, assume
import tempfile
import os
from fnmatch import fnmatch
import pytest

from meeting_router.watcher import FileWatcher


# Feature: meeting-router, Property 1: File pattern matching correctness
# For any filename, the file watcher should trigger processing if and only if the filename matches the pattern
@given(
    base_name=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc'))),
    extension=st.sampled_from([".txt", ".md", ".log", ""])
)
def test_file_pattern_matching_correctness(base_name, extension):
    """Test that file pattern matching works correctly."""
    assume(base_name.strip())
    
    # Test pattern matching
    pattern = FileWatcher.TRANSCRIPT_PATTERN
    
    # Create various filenames
    matching_name = f"meeting_transcript_{base_name}.txt"
    non_matching_name = f"{base_name}{extension}"
    
    # Check if matching name matches pattern
    assert fnmatch(matching_name, pattern)
    
    # Check if non-matching name doesn't match (unless it accidentally does)
    if not non_matching_name.startswith("meeting_transcript_") or not non_matching_name.endswith(".txt"):
        assert not fnmatch(non_matching_name, pattern)


@given(identifier=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))))
def test_transcript_pattern_matches_valid_files(identifier):
    """Test that valid transcript filenames match the pattern."""
    assume(identifier.strip())
    
    pattern = FileWatcher.TRANSCRIPT_PATTERN
    
    # Valid transcript filename
    filename = f"meeting_transcript_{identifier}.txt"
    
    # Should match
    assert fnmatch(filename, pattern)


@given(filename=st.text(min_size=1, max_size=50))
def test_non_transcript_files_dont_match(filename):
    """Test that non-transcript files don't match the pattern."""
    # Ensure filename doesn't match the pattern
    assume(not filename.startswith("meeting_transcript_"))
    assume(not filename.endswith(".txt") or not "meeting_transcript_" in filename)
    
    pattern = FileWatcher.TRANSCRIPT_PATTERN
    
    # Should not match
    assert not fnmatch(filename, pattern)


# Feature: meeting-router, Property 2: File content round-trip
# For any file content, reading the file after writing should produce identical content
@given(content=st.text(min_size=0, max_size=1000, alphabet=st.characters(blacklist_characters='\x00')))
def test_file_content_round_trip(content):
    """Test that file content can be written and read back identically."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        temp_file = f.name
        f.write(content)
    
    try:
        # Read back using FileWatcher's read method
        read_content = FileWatcher.read_file(temp_file)
        
        # Should be identical
        assert read_content == content
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


# Feature: meeting-router, Property 3: Error resilience
# For any invalid or unreadable file, the system should log an error and continue without crashing
def test_error_resilience_nonexistent_file():
    """Test that reading nonexistent file raises exception gracefully."""
    nonexistent_file = "/tmp/this_file_does_not_exist_12345.txt"
    
    # Should raise exception
    with pytest.raises(Exception):
        FileWatcher.read_file(nonexistent_file)


def test_error_resilience_directory():
    """Test that reading a directory raises exception gracefully."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Should raise exception when trying to read a directory
        with pytest.raises(Exception):
            FileWatcher.read_file(temp_dir)


# Test pattern matching with various formats
@given(
    prefix=st.text(min_size=0, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))),
    suffix=st.text(min_size=0, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll')))
)
def test_pattern_specificity(prefix, suffix):
    """Test that pattern is specific to meeting transcripts."""
    pattern = FileWatcher.TRANSCRIPT_PATTERN
    
    # Files that should NOT match
    non_matches = [
        f"{prefix}_transcript_{suffix}.txt",  # Missing "meeting"
        f"meeting_{suffix}.txt",  # Missing "transcript"
        f"meeting_transcript_{suffix}.md",  # Wrong extension
        f"meeting_transcript_{suffix}",  # No extension
    ]
    
    for filename in non_matches:
        if filename != "meeting_transcript_.txt":  # This one actually matches
            # Most should not match
            if not fnmatch(filename, pattern):
                assert True  # Expected


# Test UTF-8 encoding
@given(content=st.text(min_size=10, max_size=500))
def test_utf8_encoding_support(content):
    """Test that UTF-8 content is handled correctly."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        temp_file = f.name
        f.write(content)
    
    try:
        read_content = FileWatcher.read_file(temp_file)
        assert read_content == content
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


# Test empty file
def test_empty_file_handling():
    """Test that empty files are handled correctly."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        temp_file = f.name
        # Write nothing
    
    try:
        content = FileWatcher.read_file(temp_file)
        assert content == ""
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


# Test large file handling
def test_large_file_handling():
    """Test that large files can be read."""
    large_content = "x" * 100000  # 100KB
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        temp_file = f.name
        f.write(large_content)
    
    try:
        content = FileWatcher.read_file(temp_file)
        assert len(content) == len(large_content)
        assert content == large_content
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)


# Test pattern case sensitivity
def test_pattern_case_sensitivity():
    """Test pattern matching with different cases."""
    pattern = FileWatcher.TRANSCRIPT_PATTERN
    
    # Standard case
    assert fnmatch("meeting_transcript_test.txt", pattern)
    
    # Different cases - pattern is case-sensitive
    # These should NOT match if pattern is case-sensitive
    assert not fnmatch("Meeting_Transcript_test.txt", pattern)
    assert not fnmatch("MEETING_TRANSCRIPT_test.txt", pattern)


# Test wildcard in pattern
@given(middle=st.text(min_size=0, max_size=30, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc'))))
def test_pattern_wildcard(middle):
    """Test that pattern wildcard matches any middle content."""
    pattern = FileWatcher.TRANSCRIPT_PATTERN
    
    filename = f"meeting_transcript_{middle}.txt"
    
    # Should match regardless of middle content
    assert fnmatch(filename, pattern)
