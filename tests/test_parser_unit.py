"""Unit tests for transcript parser."""

import pytest
from meeting_router.parser import TranscriptParser


def test_parse_well_formed_transcript():
    """Test parsing of a well-formed transcript."""
    parser = TranscriptParser()
    
    transcript = """Speaker 1: Welcome everyone to today's standup.
Jane: Thanks. I will finish the API integration by Friday.
John Doe: I need to review Jane's PR. Also, we decided to use PostgreSQL for the new feature.
Speaker 1: Sounds good. Someone should update the documentation."""
    
    segments = parser.parse(transcript)
    
    assert len(segments) == 4
    assert segments[0].speaker == "Speaker 1"
    assert "Welcome everyone" in segments[0].text
    
    assert segments[1].speaker == "Jane"
    assert "API integration" in segments[1].text
    
    assert segments[2].speaker == "John Doe"
    assert "PostgreSQL" in segments[2].text
    
    assert segments[3].speaker == "Speaker 1"
    assert "documentation" in segments[3].text


def test_parse_various_speaker_formats():
    """Test handling of various speaker name formats."""
    parser = TranscriptParser()
    
    transcript = """Speaker 1: First speaker.
Jane: Second speaker.
John Doe: Third speaker.
J. Smith: Fourth speaker.
Dr. Brown: Fifth speaker."""
    
    segments = parser.parse(transcript)
    
    assert len(segments) == 5
    assert segments[0].speaker == "Speaker 1"
    assert segments[1].speaker == "Jane"
    assert segments[2].speaker == "John Doe"
    assert segments[3].speaker == "J. Smith"
    assert segments[4].speaker == "Dr. Brown"


def test_parse_multi_line_segments():
    """Test parsing of multi-line speaker segments."""
    parser = TranscriptParser()
    
    transcript = """Alice: This is the first line.
This is the second line.
And this is the third line.
Bob: Now Bob is speaking."""
    
    segments = parser.parse(transcript)
    
    assert len(segments) == 2
    assert segments[0].speaker == "Alice"
    assert "first line" in segments[0].text
    assert "second line" in segments[0].text
    assert "third line" in segments[0].text
    
    assert segments[1].speaker == "Bob"
    assert "Bob is speaking" in segments[1].text


def test_parse_empty_transcript():
    """Test parsing of empty transcript."""
    parser = TranscriptParser()
    
    segments = parser.parse("")
    assert segments == []
    
    segments = parser.parse("   ")
    assert segments == []
    
    segments = parser.parse("\n\n\n")
    assert segments == []


def test_speaker_name_normalization():
    """Test that speaker names are normalized consistently."""
    parser = TranscriptParser()
    
    transcript = """john doe: First statement.
JOHN DOE: Second statement.
  John Doe  : Third statement."""
    
    segments = parser.parse(transcript)
    
    # All should be normalized to the same format
    assert len(segments) == 3
    for segment in segments:
        assert segment.speaker == "John Doe"


def test_parse_with_colons_in_dialogue():
    """Test that colons in dialogue don't break parsing."""
    parser = TranscriptParser()
    
    transcript = """Alice: The time is 3:30 PM.
Bob: Here's the URL: https://example.com"""
    
    segments = parser.parse(transcript)
    
    assert len(segments) == 2
    assert segments[0].speaker == "Alice"
    assert "3:30 PM" in segments[0].text
    
    assert segments[1].speaker == "Bob"
    assert "https://example.com" in segments[1].text


def test_parse_with_empty_lines():
    """Test parsing with empty lines between segments."""
    parser = TranscriptParser()
    
    transcript = """Alice: First statement.

Bob: Second statement.


Charlie: Third statement."""
    
    segments = parser.parse(transcript)
    
    assert len(segments) == 3
    assert segments[0].speaker == "Alice"
    assert segments[1].speaker == "Bob"
    assert segments[2].speaker == "Charlie"


def test_parse_single_speaker():
    """Test parsing with only one speaker."""
    parser = TranscriptParser()
    
    transcript = """Alice: This is a monologue.
It continues here.
And here too."""
    
    segments = parser.parse(transcript)
    
    assert len(segments) == 1
    assert segments[0].speaker == "Alice"
    assert "monologue" in segments[0].text
    assert "continues here" in segments[0].text


def test_parse_with_numbers_in_names():
    """Test parsing speaker names with numbers."""
    parser = TranscriptParser()
    
    transcript = """Speaker 1: First.
Speaker 2: Second.
Speaker 10: Tenth."""
    
    segments = parser.parse(transcript)
    
    assert len(segments) == 3
    assert segments[0].speaker == "Speaker 1"
    assert segments[1].speaker == "Speaker 2"
    assert segments[2].speaker == "Speaker 10"


def test_parse_preserves_start_position():
    """Test that start positions are tracked."""
    parser = TranscriptParser()
    
    transcript = """Alice: First.
Bob: Second."""
    
    segments = parser.parse(transcript)
    
    assert len(segments) == 2
    assert segments[0].start_position >= 0
    assert segments[1].start_position > segments[0].start_position


def test_parse_with_special_characters():
    """Test parsing with special characters in dialogue."""
    parser = TranscriptParser()
    
    transcript = """Alice: Hello! How are you?
Bob: I'm fine, thanks. What about you?
Charlie: Great! Let's get started..."""
    
    segments = parser.parse(transcript)
    
    assert len(segments) == 3
    assert "Hello!" in segments[0].text
    assert "I'm fine" in segments[1].text
    assert "Great!" in segments[2].text
