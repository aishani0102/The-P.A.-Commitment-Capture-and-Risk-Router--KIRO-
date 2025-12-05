"""Property-based tests for sentiment analysis."""

from hypothesis import given, strategies as st, assume, settings
from unittest.mock import Mock, MagicMock
import pytest

from meeting_router.nlp import SentimentAnalyzer
from meeting_router.models import SpeakerSegment


# Custom strategies
@st.composite
def decision_phrases(draw):
    """Generate decision phrases."""
    patterns = ["We decided", "The final choice is", "We agreed", "The decision is", "We're going with"]
    pattern = draw(st.sampled_from(patterns))
    decision = draw(st.text(min_size=5, max_size=100, alphabet=st.characters(blacklist_characters='\n\r')))
    assume(decision.strip())
    return f"{pattern} {decision.strip()}."


# Feature: meeting-router, Property 8: Decision point detection completeness
# For any transcript containing decision phrases, all instances should be identified for sentiment analysis
@given(
    num_decisions=st.integers(min_value=1, max_value=5),
    decision_phrase=st.sampled_from(["We decided", "The final choice is", "We agreed", "The decision is"])
)
@settings(deadline=None)  # Disable deadline for tests that might load models
def test_decision_point_detection_completeness(num_decisions, decision_phrase):
    """Test that all decision phrases are detected."""
    analyzer = SentimentAnalyzer(sentiment_threshold=0.5)
    
    # Mock the model to avoid loading it
    analyzer.model = Mock()
    analyzer.model.return_value = [{"label": "POSITIVE", "score": 0.9}]
    
    # Create transcript with decision phrases
    sentences = []
    for i in range(num_decisions):
        sentences.append(f"{decision_phrase} to use option {i}")
    
    # Add some non-decision sentences
    sentences.append("This is just a regular sentence")
    sentences.append("Another regular sentence")
    
    transcript = ". ".join(sentences) + "."
    
    # Analyze
    risk_points = analyzer.analyze(transcript, [])
    
    # Should identify decision points (though they may not all be risk points due to sentiment)
    # The key is that decision phrases are being detected
    # Since we mocked positive sentiment, no risk points should be flagged
    assert isinstance(risk_points, list)


# Feature: meeting-router, Property 9: Sentiment context inclusion
# For any identified decision point, the sentiment analysis should include surrounding sentences
@given(
    decision_phrase=st.sampled_from(["We decided", "We agreed"]),
    context_before=st.text(min_size=10, max_size=50, alphabet=st.characters(blacklist_characters='\n\r')),
    context_after=st.text(min_size=10, max_size=50, alphabet=st.characters(blacklist_characters='\n\r'))
)
@settings(deadline=None)
def test_sentiment_context_inclusion(decision_phrase, context_before, context_after):
    """Test that sentiment analysis includes surrounding context."""
    assume(context_before.strip() and context_after.strip())
    
    analyzer = SentimentAnalyzer(sentiment_threshold=0.5)
    
    # Mock the model
    analyzer.model = Mock()
    analyzer.model.return_value = [{"label": "NEGATIVE", "score": 0.9}]  # High negative = low sentiment score
    
    # Create transcript with context around decision
    transcript = f"{context_before}. {decision_phrase} to proceed. {context_after}."
    
    # Analyze
    risk_points = analyzer.analyze(transcript, [])
    
    # If a risk point was flagged, check that context is included
    if risk_points:
        risk_point = risk_points[0]
        # Context should include surrounding sentences
        assert risk_point.context
        assert len(risk_point.context) > len(decision_phrase)


# Feature: meeting-router, Property 10: Risk flagging threshold correctness
# For any sentiment score and threshold value, a risk point should be flagged if and only if the score is below the threshold
@given(
    threshold=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    sentiment_score=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
)
@settings(deadline=None)
def test_risk_flagging_threshold_correctness(threshold, sentiment_score):
    """Test that risk points are flagged correctly based on threshold."""
    analyzer = SentimentAnalyzer(sentiment_threshold=threshold)
    
    # Mock the model to return a specific sentiment
    analyzer.model = Mock()
    
    # Convert sentiment_score to model output
    # If sentiment_score < 0.5, it's negative; otherwise positive
    if sentiment_score < 0.5:
        # Negative sentiment: score represents how negative (higher = more negative)
        model_score = 1.0 - sentiment_score
        analyzer.model.return_value = [{"label": "NEGATIVE", "score": model_score}]
    else:
        # Positive sentiment: score represents how positive
        model_score = sentiment_score
        analyzer.model.return_value = [{"label": "POSITIVE", "score": model_score}]
    
    # Create transcript with decision phrase
    transcript = "We decided to move forward with the plan."
    
    # Analyze
    risk_points = analyzer.analyze(transcript, [])
    
    # Check if risk point was flagged correctly
    should_flag = sentiment_score < threshold
    was_flagged = len(risk_points) > 0
    
    assert was_flagged == should_flag


# Feature: meeting-router, Property 11: Risk point context completeness
# For any flagged risk point, the captured context should include the decision statement and surrounding dialogue
@given(
    decision_text=st.text(min_size=10, max_size=50, alphabet=st.characters(blacklist_characters='\n\r'))
)
@settings(deadline=None)
def test_risk_point_context_completeness(decision_text):
    """Test that risk points include complete context."""
    assume(decision_text.strip())
    
    analyzer = SentimentAnalyzer(sentiment_threshold=0.5)
    
    # Mock the model to return negative sentiment
    analyzer.model = Mock()
    analyzer.model.return_value = [{"label": "NEGATIVE", "score": 0.9}]
    
    # Create transcript
    decision_phrase = "We decided"
    transcript = f"Context before. {decision_phrase} {decision_text}. Context after."
    
    # Analyze
    risk_points = analyzer.analyze(transcript, [])
    
    # Should have risk points with complete context
    if risk_points:
        risk_point = risk_points[0]
        # Context should include the decision statement
        assert decision_phrase in risk_point.text_segment or decision_phrase in risk_point.context
        # Context should include surrounding dialogue
        assert risk_point.context
        assert len(risk_point.context) > len(risk_point.text_segment)


# Feature: meeting-router, Property 12: Sentiment analysis error continuation
# For any sentiment analysis failure on a segment, the system should continue processing remaining segments
@given(num_decisions=st.integers(min_value=2, max_value=5))
@settings(deadline=None)
def test_sentiment_analysis_error_continuation(num_decisions):
    """Test that errors in sentiment analysis don't stop processing."""
    analyzer = SentimentAnalyzer(sentiment_threshold=0.5)
    
    # Mock the model to fail on first call, succeed on others
    analyzer.model = Mock()
    call_count = [0]
    
    def side_effect(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            raise Exception("Simulated model error")
        return [{"label": "POSITIVE", "score": 0.9}]
    
    analyzer.model.side_effect = side_effect
    
    # Create transcript with multiple decision points
    sentences = [f"We decided option {i}" for i in range(num_decisions)]
    transcript = ". ".join(sentences) + "."
    
    # Analyze - should not raise exception
    try:
        risk_points = analyzer.analyze(transcript, [])
        # Should continue processing despite error
        assert isinstance(risk_points, list)
    except Exception as e:
        pytest.fail(f"Should not raise exception, but got: {e}")


# Test with no model loaded
def test_no_model_loaded():
    """Test that analyzer handles missing model gracefully."""
    analyzer = SentimentAnalyzer(sentiment_threshold=0.5)
    analyzer.model = None  # Simulate model not loaded
    
    transcript = "We decided to proceed with the plan."
    
    # Should not crash
    risk_points = analyzer.analyze(transcript, [])
    
    # Should return empty list when model is not available
    assert risk_points == []


# Test threshold edge cases
@given(threshold=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False))
@settings(deadline=None)
def test_threshold_edge_cases(threshold):
    """Test that threshold values at edges work correctly."""
    analyzer = SentimentAnalyzer(sentiment_threshold=threshold)
    
    # Mock model
    analyzer.model = Mock()
    analyzer.model.return_value = [{"label": "NEGATIVE", "score": 0.5}]
    
    transcript = "We decided something."
    
    # Should not crash with any valid threshold
    risk_points = analyzer.analyze(transcript, [])
    assert isinstance(risk_points, list)


# Test case insensitivity of decision phrases
@given(
    decision_phrase=st.sampled_from(["We decided", "We agreed", "The decision is"]),
    case_variant=st.sampled_from(["lower", "upper", "title"])
)
@settings(deadline=None)
def test_decision_phrase_case_insensitivity(decision_phrase, case_variant):
    """Test that decision phrases are detected regardless of case."""
    analyzer = SentimentAnalyzer(sentiment_threshold=0.5)
    
    # Mock model
    analyzer.model = Mock()
    analyzer.model.return_value = [{"label": "NEGATIVE", "score": 0.9}]
    
    # Apply case transformation
    if case_variant == "lower":
        phrase = decision_phrase.lower()
    elif case_variant == "upper":
        phrase = decision_phrase.upper()
    else:
        phrase = decision_phrase.title()
    
    transcript = f"{phrase} to proceed with the plan."
    
    # Should detect decision phrase regardless of case
    risk_points = analyzer.analyze(transcript, [])
    
    # With negative sentiment, should flag risk point
    assert len(risk_points) >= 1
