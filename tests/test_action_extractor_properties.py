"""Property-based tests for action item extraction."""

from hypothesis import given, strategies as st, assume
import pytest

from meeting_router.nlp import ActionItemExtractor
from meeting_router.models import SpeakerSegment


# Custom strategies
@st.composite
def action_phrases(draw):
    """Generate action item phrases."""
    patterns = ["I will", "I'll", "Need to", "Let's follow up on", "Someone should", "We need to", "I can", "I should"]
    pattern = draw(st.sampled_from(patterns))
    task = draw(st.text(min_size=3, max_size=100, alphabet=st.characters(blacklist_characters='\n\r')))
    assume(task.strip())
    return f"{pattern} {task.strip()}"


@st.composite
def speaker_segments_with_actions(draw):
    """Generate speaker segments containing action items."""
    speaker = draw(st.text(min_size=1, max_size=30, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Zs'))))
    assume(speaker.strip())
    
    num_actions = draw(st.integers(min_value=1, max_value=5))
    actions = [draw(action_phrases()) for _ in range(num_actions)]
    
    # Combine actions into text with separators
    text = ". ".join(actions) + "."
    
    return SpeakerSegment(
        speaker=speaker.strip(),
        text=text,
        start_position=0
    ), num_actions


# Feature: meeting-router, Property 4: Action pattern detection completeness
# For any transcript containing action phrases, all instances should be identified by the extractor
@given(
    num_segments=st.integers(min_value=1, max_value=5),
    action_phrase=st.sampled_from(["I will", "I'll", "Need to", "Let's follow up on", "Someone should", "We need to", "I can", "I should"])
)
def test_action_pattern_detection_completeness(num_segments, action_phrase):
    """Test that all action phrases are detected."""
    extractor = ActionItemExtractor()
    
    # Create segments with action phrases
    segments = []
    total_expected = 0
    
    for i in range(num_segments):
        task = f"complete task {i}"
        text = f"{action_phrase} {task}."
        segments.append(SpeakerSegment(
            speaker=f"Speaker{i}",
            text=text,
            start_position=i * 100
        ))
        total_expected += 1
    
    # Extract action items
    action_items = extractor.extract(segments)
    
    # Should find all action items
    assert len(action_items) == total_expected


@given(segments_data=st.lists(speaker_segments_with_actions(), min_size=1, max_size=5))
def test_all_action_phrases_detected(segments_data):
    """Test that all action phrases in segments are detected."""
    extractor = ActionItemExtractor()
    
    segments = [seg for seg, _ in segments_data]
    expected_count = sum(count for _, count in segments_data)
    
    action_items = extractor.extract(segments)
    
    # Should detect all action items
    assert len(action_items) == expected_count


# Feature: meeting-router, Property 5: Task description extraction completeness
# For any detected action item phrase, the extracted task description should be non-empty and contain relevant context
@given(
    action_phrase=st.sampled_from(["I will", "Need to", "Someone should"]),
    task_description=st.text(min_size=5, max_size=100, alphabet=st.characters(blacklist_characters='\n\r'))
)
def test_task_description_extraction_completeness(action_phrase, task_description):
    """Test that task descriptions are extracted and non-empty."""
    assume(task_description.strip())
    
    extractor = ActionItemExtractor()
    
    text = f"{action_phrase} {task_description}."
    segment = SpeakerSegment(speaker="Alice", text=text, start_position=0)
    
    action_items = extractor.extract([segment])
    
    # Should extract one action item
    assert len(action_items) == 1
    
    # Task description should be non-empty
    assert action_items[0].task_description
    assert len(action_items[0].task_description.strip()) > 0
    
    # Should contain relevant context from original text
    # The task description should be related to the input
    assert action_items[0].task_description.strip() in task_description or \
           task_description.strip().startswith(action_items[0].task_description.strip())


# Feature: meeting-router, Property 6: Owner attribution correctness
# For any action item extracted from a speaker segment, the owner should match the speaker of that segment
@given(
    speaker=st.text(min_size=1, max_size=30, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Zs'))),
    action_phrase=st.sampled_from(["I will", "Need to", "Someone should"]),
    task=st.text(min_size=3, max_size=50, alphabet=st.characters(blacklist_characters='\n\r'))
)
def test_owner_attribution_correctness(speaker, action_phrase, task):
    """Test that action items are attributed to the correct speaker."""
    assume(speaker.strip() and task.strip())
    
    extractor = ActionItemExtractor()
    
    text = f"{action_phrase} {task}."
    segment = SpeakerSegment(speaker=speaker.strip(), text=text, start_position=0)
    
    action_items = extractor.extract([segment])
    
    # Should have one action item
    assert len(action_items) >= 1
    
    # Owner should match the speaker
    for action_item in action_items:
        assert action_item.owner == speaker.strip()


@given(
    speakers=st.lists(
        st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))),
        min_size=2,
        max_size=5,
        unique=True
    )
)
def test_owner_attribution_multiple_speakers(speakers):
    """Test that action items from different speakers are attributed correctly."""
    extractor = ActionItemExtractor()
    
    segments = []
    for speaker in speakers:
        text = f"I will complete my task for {speaker}."
        segments.append(SpeakerSegment(speaker=speaker, text=text, start_position=0))
    
    action_items = extractor.extract(segments)
    
    # Should have one action item per speaker
    assert len(action_items) == len(speakers)
    
    # Each action item should be attributed to the correct speaker
    for i, action_item in enumerate(action_items):
        assert action_item.owner == speakers[i]


# Feature: meeting-router, Property 7: Multiple action items per speaker
# For any speaker segment containing N action item phrases, exactly N action items should be extracted, all with the same owner
@given(
    speaker=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))),
    num_actions=st.integers(min_value=1, max_value=5)
)
def test_multiple_action_items_per_speaker(speaker, num_actions):
    """Test that multiple action items from one speaker are all extracted with the same owner."""
    assume(speaker.strip())
    
    extractor = ActionItemExtractor()
    
    # Create text with multiple action items
    action_phrases = ["I will", "Need to", "I should", "I can", "We need to"]
    sentences = []
    for i in range(num_actions):
        phrase = action_phrases[i % len(action_phrases)]
        sentences.append(f"{phrase} do task {i}")
    
    text = ". ".join(sentences) + "."
    segment = SpeakerSegment(speaker=speaker.strip(), text=text, start_position=0)
    
    action_items = extractor.extract([segment])
    
    # Should extract exactly N action items
    assert len(action_items) == num_actions
    
    # All should have the same owner
    for action_item in action_items:
        assert action_item.owner == speaker.strip()


@given(segment_data=speaker_segments_with_actions())
def test_multiple_actions_same_owner_property(segment_data):
    """Property test for multiple actions per speaker."""
    segment, expected_count = segment_data
    
    extractor = ActionItemExtractor()
    action_items = extractor.extract([segment])
    
    # Should extract the expected number of action items
    assert len(action_items) == expected_count
    
    # All should have the same owner
    if action_items:
        expected_owner = segment.speaker
        for action_item in action_items:
            assert action_item.owner == expected_owner


# Test context quote preservation
@given(
    speaker=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))),
    action_phrase=st.sampled_from(["I will", "Need to"]),
    task=st.text(min_size=5, max_size=50, alphabet=st.characters(blacklist_characters='\n\r'))
)
def test_context_quote_preservation(speaker, action_phrase, task):
    """Test that context quotes are preserved."""
    assume(speaker.strip() and task.strip())
    
    extractor = ActionItemExtractor()
    
    text = f"{action_phrase} {task}."
    segment = SpeakerSegment(speaker=speaker.strip(), text=text, start_position=0)
    
    action_items = extractor.extract([segment])
    
    # Should have action items with context quotes
    assert len(action_items) >= 1
    for action_item in action_items:
        assert action_item.context_quote
        assert len(action_item.context_quote) > 0


# Test case insensitivity
@given(
    action_phrase=st.sampled_from(["I will", "Need to", "Someone should"]),
    case_variant=st.sampled_from(["lower", "upper", "title"])
)
def test_case_insensitive_detection(action_phrase, case_variant):
    """Test that action phrases are detected regardless of case."""
    extractor = ActionItemExtractor()
    
    # Apply case transformation
    if case_variant == "lower":
        phrase = action_phrase.lower()
    elif case_variant == "upper":
        phrase = action_phrase.upper()
    else:
        phrase = action_phrase.title()
    
    text = f"{phrase} complete the task."
    segment = SpeakerSegment(speaker="Alice", text=text, start_position=0)
    
    action_items = extractor.extract([segment])
    
    # Should detect the action item regardless of case
    assert len(action_items) >= 1
