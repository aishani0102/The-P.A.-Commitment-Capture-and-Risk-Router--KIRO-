"""Unit tests for action item extraction."""

import pytest
from meeting_router.nlp import ActionItemExtractor
from meeting_router.models import SpeakerSegment


def test_extract_i_will_pattern():
    """Test extraction of 'I will' pattern."""
    extractor = ActionItemExtractor()
    
    segment = SpeakerSegment(
        speaker="Alice",
        text="I will finish the report by Friday.",
        start_position=0
    )
    
    action_items = extractor.extract([segment])
    
    assert len(action_items) == 1
    assert action_items[0].owner == "Alice"
    assert "finish the report" in action_items[0].task_description


def test_extract_need_to_pattern():
    """Test extraction of 'Need to' pattern."""
    extractor = ActionItemExtractor()
    
    segment = SpeakerSegment(
        speaker="Bob",
        text="Need to review the pull request.",
        start_position=0
    )
    
    action_items = extractor.extract([segment])
    
    assert len(action_items) == 1
    assert action_items[0].owner == "Bob"
    assert "review the pull request" in action_items[0].task_description


def test_extract_lets_follow_up_pattern():
    """Test extraction of 'Let's follow up on' pattern."""
    extractor = ActionItemExtractor()
    
    segment = SpeakerSegment(
        speaker="Charlie",
        text="Let's follow up on the client feedback.",
        start_position=0
    )
    
    action_items = extractor.extract([segment])
    
    assert len(action_items) == 1
    assert action_items[0].owner == "Charlie"
    assert "client feedback" in action_items[0].task_description


def test_extract_someone_should_pattern():
    """Test extraction of 'Someone should' pattern."""
    extractor = ActionItemExtractor()
    
    segment = SpeakerSegment(
        speaker="David",
        text="Someone should update the documentation.",
        start_position=0
    )
    
    action_items = extractor.extract([segment])
    
    assert len(action_items) == 1
    assert action_items[0].owner == "David"
    assert "update the documentation" in action_items[0].task_description


def test_extract_multiple_actions_same_speaker():
    """Test extraction of multiple action items from the same speaker."""
    extractor = ActionItemExtractor()
    
    segment = SpeakerSegment(
        speaker="Eve",
        text="I will finish the API integration. I also need to write tests.",
        start_position=0
    )
    
    action_items = extractor.extract([segment])
    
    assert len(action_items) == 2
    assert all(item.owner == "Eve" for item in action_items)
    assert any("API integration" in item.task_description for item in action_items)
    assert any("write tests" in item.task_description for item in action_items)


def test_extract_from_multiple_speakers():
    """Test extraction from multiple speakers."""
    extractor = ActionItemExtractor()
    
    segments = [
        SpeakerSegment(speaker="Alice", text="I will do task A.", start_position=0),
        SpeakerSegment(speaker="Bob", text="I will do task B.", start_position=100),
        SpeakerSegment(speaker="Charlie", text="I will do task C.", start_position=200),
    ]
    
    action_items = extractor.extract(segments)
    
    assert len(action_items) == 3
    assert action_items[0].owner == "Alice"
    assert action_items[1].owner == "Bob"
    assert action_items[2].owner == "Charlie"


def test_no_action_items():
    """Test segment with no action items."""
    extractor = ActionItemExtractor()
    
    segment = SpeakerSegment(
        speaker="Frank",
        text="This is just a regular statement without any action items.",
        start_position=0
    )
    
    action_items = extractor.extract([segment])
    
    assert len(action_items) == 0


def test_context_quote_captured():
    """Test that context quotes are captured."""
    extractor = ActionItemExtractor()
    
    segment = SpeakerSegment(
        speaker="Grace",
        text="I will complete the project by next week.",
        start_position=0
    )
    
    action_items = extractor.extract([segment])
    
    assert len(action_items) == 1
    assert action_items[0].context_quote
    assert "I will complete the project" in action_items[0].context_quote


def test_case_insensitive_matching():
    """Test that pattern matching is case insensitive."""
    extractor = ActionItemExtractor()
    
    segments = [
        SpeakerSegment(speaker="Alice", text="i will do this.", start_position=0),
        SpeakerSegment(speaker="Bob", text="I WILL do that.", start_position=100),
        SpeakerSegment(speaker="Charlie", text="I Will do something.", start_position=200),
    ]
    
    action_items = extractor.extract(segments)
    
    assert len(action_items) == 3


def test_extract_we_need_to_pattern():
    """Test extraction of 'We need to' pattern."""
    extractor = ActionItemExtractor()
    
    segment = SpeakerSegment(
        speaker="Helen",
        text="We need to schedule a follow-up meeting.",
        start_position=0
    )
    
    action_items = extractor.extract([segment])
    
    assert len(action_items) == 1
    assert action_items[0].owner == "Helen"
    assert "schedule a follow-up meeting" in action_items[0].task_description


def test_extract_i_can_pattern():
    """Test extraction of 'I can' pattern."""
    extractor = ActionItemExtractor()
    
    segment = SpeakerSegment(
        speaker="Ian",
        text="I can handle the deployment.",
        start_position=0
    )
    
    action_items = extractor.extract([segment])
    
    assert len(action_items) == 1
    assert action_items[0].owner == "Ian"
    assert "handle the deployment" in action_items[0].task_description


def test_extract_i_should_pattern():
    """Test extraction of 'I should' pattern."""
    extractor = ActionItemExtractor()
    
    segment = SpeakerSegment(
        speaker="Julia",
        text="I should review the code before merging.",
        start_position=0
    )
    
    action_items = extractor.extract([segment])
    
    assert len(action_items) == 1
    assert action_items[0].owner == "Julia"
    assert "review the code" in action_items[0].task_description


def test_quoted_context_included():
    """Test that action items in quoted or hypothetical contexts are included."""
    extractor = ActionItemExtractor()
    
    segment = SpeakerSegment(
        speaker="Kevin",
        text='He said "I will finish this tomorrow" but I\'m not sure.',
        start_position=0
    )
    
    action_items = extractor.extract([segment])
    
    # Conservative approach: include quoted action items
    assert len(action_items) >= 1


def test_empty_segment_list():
    """Test extraction from empty segment list."""
    extractor = ActionItemExtractor()
    
    action_items = extractor.extract([])
    
    assert action_items == []


def test_trailing_punctuation_removed():
    """Test that trailing punctuation is removed from task descriptions."""
    extractor = ActionItemExtractor()
    
    segment = SpeakerSegment(
        speaker="Laura",
        text="I will complete the task, and then move on.",
        start_position=0
    )
    
    action_items = extractor.extract([segment])
    
    assert len(action_items) >= 1
    # Task description should not end with comma
    assert not action_items[0].task_description.endswith(',')
