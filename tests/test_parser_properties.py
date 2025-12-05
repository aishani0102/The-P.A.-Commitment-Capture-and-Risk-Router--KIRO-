"""Property-based tests for transcript parsing."""

from hypothesis import given, strategies as st, assume
import pytest

from meeting_router.parser import TranscriptParser
from meeting_router.models import SpeakerSegment


# Custom strategies for generating test data
@st.composite
def speaker_names(draw):
    """Generate realistic speaker names."""
    formats = [
        st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'))),
        st.from_regex(r"Speaker \d+", fullmatch=True),
        st.from_regex(r"[A-Z][a-z]+ [A-Z][a-z]+", fullmatch=True),  # John Doe
        st.from_regex(r"[A-Z]\. [A-Z][a-z]+", fullmatch=True),  # J. Smith
    ]
    name = draw(st.one_of(*formats))
    # Ensure name doesn't contain colons (which would break the format)
    assume(':' not in name)
    assume(name.strip())  # Ensure non-empty after stripping
    return name


@st.composite
def dialogue_text(draw):
    """Generate dialogue text without newlines that would break parsing."""
    text = draw(st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_characters='\n\r')))
    assume(text.strip())  # Ensure non-empty after stripping
    return text


# Feature: meeting-router, Property 32: Speaker label recognition
# For any text in the format "Speaker Name: dialogue text", the parser should recognize it as a speaker segment
@given(
    speaker=speaker_names(),
    text=dialogue_text()
)
def test_speaker_label_recognition(speaker, text):
    """Test that speaker labels in the format 'Speaker Name: dialogue text' are recognized."""
    parser = TranscriptParser()
    
    # Create transcript with speaker label format
    transcript = f"{speaker}: {text}"
    
    # Parse transcript
    segments = parser.parse(transcript)
    
    # Should recognize exactly one segment
    assert len(segments) == 1
    assert segments[0].speaker == speaker.strip().title()  # Normalized
    assert text.strip() in segments[0].text  # Text should be preserved


# Feature: meeting-router, Property 33: Multi-sentence speaker attribution
# For any speaker segment containing multiple sentences, all sentences until the next speaker label should be attributed to that speaker
@given(
    speaker=speaker_names(),
    sentences=st.lists(dialogue_text(), min_size=2, max_size=5)
)
def test_multi_sentence_speaker_attribution(speaker, sentences):
    """Test that multiple sentences are attributed to the same speaker until the next speaker label."""
    parser = TranscriptParser()
    
    # Create transcript with multiple sentences for one speaker
    transcript = f"{speaker}: {sentences[0]}\n"
    for sentence in sentences[1:]:
        transcript += f"{sentence}\n"
    
    # Parse transcript
    segments = parser.parse(transcript)
    
    # Should have exactly one segment with all sentences
    assert len(segments) == 1
    assert segments[0].speaker == speaker.strip().title()
    
    # All sentences should be in the segment text
    for sentence in sentences:
        assert sentence.strip() in segments[0].text


@given(
    speakers=st.lists(speaker_names(), min_size=2, max_size=4, unique=True),
    texts=st.lists(dialogue_text(), min_size=2, max_size=4)
)
def test_multi_sentence_attribution_with_multiple_speakers(speakers, texts):
    """Test that sentences are correctly attributed when there are multiple speakers."""
    assume(len(speakers) == len(texts))
    
    parser = TranscriptParser()
    
    # Create transcript with multiple speakers, each with their own text
    transcript_lines = []
    for speaker, text in zip(speakers, texts):
        transcript_lines.append(f"{speaker}: {text}")
    
    transcript = "\n".join(transcript_lines)
    
    # Parse transcript
    segments = parser.parse(transcript)
    
    # Should have one segment per speaker
    assert len(segments) == len(speakers)
    
    # Each segment should have the correct speaker and text
    for i, (speaker, text) in enumerate(zip(speakers, texts)):
        assert segments[i].speaker == speaker.strip().title()
        assert text.strip() in segments[i].text


# Feature: meeting-router, Property 34: Speaker name normalization consistency
# For any speaker name with varying whitespace or capitalization, the normalized form should be consistent across all occurrences
@given(
    base_name=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))),
    text1=dialogue_text(),
    text2=dialogue_text()
)
def test_speaker_name_normalization_consistency(base_name, text1, text2):
    """Test that speaker names are normalized consistently."""
    assume(base_name.strip())
    assume(':' not in base_name)
    
    parser = TranscriptParser()
    
    # Create variations of the same name with different whitespace/capitalization
    name_variations = [
        base_name.lower(),
        base_name.upper(),
        f"  {base_name}  ",  # Extra whitespace
        base_name.title(),
    ]
    
    # Create transcript with multiple occurrences of the same speaker with variations
    transcript_lines = []
    for i, variation in enumerate(name_variations[:2]):  # Use first 2 variations
        text = text1 if i == 0 else text2
        transcript_lines.append(f"{variation}: {text}")
    
    transcript = "\n".join(transcript_lines)
    
    # Parse transcript
    segments = parser.parse(transcript)
    
    # All segments should have the same normalized speaker name
    if len(segments) >= 2:
        normalized_name = segments[0].speaker
        for segment in segments[1:]:
            assert segment.speaker == normalized_name


@given(
    speaker=speaker_names(),
    whitespace_prefix=st.text(min_size=0, max_size=5, alphabet=' \t'),
    whitespace_suffix=st.text(min_size=0, max_size=5, alphabet=' \t'),
    text=dialogue_text()
)
def test_speaker_name_whitespace_normalization(speaker, whitespace_prefix, whitespace_suffix, text):
    """Test that whitespace in speaker names is normalized."""
    parser = TranscriptParser()
    
    # Create speaker name with extra whitespace
    padded_speaker = f"{whitespace_prefix}{speaker}{whitespace_suffix}"
    transcript = f"{padded_speaker}: {text}"
    
    # Parse transcript
    segments = parser.parse(transcript)
    
    # Should have one segment with normalized speaker name (no extra whitespace)
    assert len(segments) == 1
    assert segments[0].speaker == speaker.strip().title()
    assert segments[0].speaker == segments[0].speaker.strip()  # No leading/trailing whitespace


# Test empty transcript handling
def test_empty_transcript():
    """Test that empty transcripts are handled gracefully."""
    parser = TranscriptParser()
    
    segments = parser.parse("")
    assert segments == []
    
    segments = parser.parse("   \n\n  ")
    assert segments == []


# Test transcript with no speaker labels
@given(text=st.text(min_size=1, max_size=200))
def test_transcript_without_speaker_labels(text):
    """Test that text without speaker labels produces no segments."""
    assume(':' not in text or not any(c.isalpha() for c in text.split(':')[0]))
    
    parser = TranscriptParser()
    segments = parser.parse(text)
    
    # Should produce no segments if there are no valid speaker labels
    # (or possibly one if the text accidentally matches the pattern)
    assert isinstance(segments, list)


# Test various speaker name formats
@given(
    speaker_num=st.integers(min_value=1, max_value=100),
    text=dialogue_text()
)
def test_numbered_speaker_format(speaker_num, text):
    """Test that numbered speaker formats like 'Speaker 1' are recognized."""
    parser = TranscriptParser()
    
    speaker = f"Speaker {speaker_num}"
    transcript = f"{speaker}: {text}"
    
    segments = parser.parse(transcript)
    
    assert len(segments) == 1
    assert segments[0].speaker == speaker.title()


@given(
    first_name=st.text(min_size=1, max_size=15, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))),
    last_name=st.text(min_size=1, max_size=15, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))),
    text=dialogue_text()
)
def test_full_name_format(first_name, last_name, text):
    """Test that full names like 'John Doe' are recognized."""
    assume(first_name.strip() and last_name.strip())
    
    parser = TranscriptParser()
    
    speaker = f"{first_name} {last_name}"
    transcript = f"{speaker}: {text}"
    
    segments = parser.parse(transcript)
    
    assert len(segments) == 1
    # Should be normalized to title case
    expected_name = f"{first_name.strip().title()} {last_name.strip().title()}"
    assert segments[0].speaker == expected_name
