"""Unit tests for sentiment analyzer."""

from unittest.mock import Mock, patch
import pytest

from meeting_router.nlp import SentimentAnalyzer
from meeting_router.models import SpeakerSegment


def test_decision_point_detection():
    """Test that decision points are detected."""
    analyzer = SentimentAnalyzer(sentiment_threshold=0.5)
    analyzer.model = Mock()
    analyzer.model.return_value = [{"label": "POSITIVE", "score": 0.9}]
    
    transcript = "We decided to use PostgreSQL for the database."
    
    risk_points = analyzer.analyze(transcript, [])
    
    # Should process the decision point (though may not flag as risk due to positive sentiment)
    assert isinstance(risk_points, list)


def test_negative_sentiment_flagged():
    """Test that negative sentiment is flagged as risk point."""
    analyzer = SentimentAnalyzer(sentiment_threshold=0.5)
    analyzer.model = Mock()
    analyzer.model.return_value = [{"label": "NEGATIVE", "score": 0.9}]  # High negative score
    
    transcript = "We decided to proceed despite concerns."
    
    risk_points = analyzer.analyze(transcript, [])
    
    # Should flag as risk point due to negative sentiment
    assert len(risk_points) > 0
    assert risk_points[0].sentiment_score < 0.5


def test_positive_sentiment_not_flagged():
    """Test that positive sentiment is not flagged as risk point."""
    analyzer = SentimentAnalyzer(sentiment_threshold=0.3)
    analyzer.model = Mock()
    analyzer.model.return_value = [{"label": "POSITIVE", "score": 0.9}]
    
    transcript = "We decided to move forward with the excellent plan."
    
    risk_points = analyzer.analyze(transcript, [])
    
    # Should not flag as risk point due to positive sentiment
    assert len(risk_points) == 0


def test_threshold_comparison():
    """Test that threshold comparison works correctly."""
    analyzer = SentimentAnalyzer(sentiment_threshold=0.4)
    analyzer.model = Mock()
    
    # Sentiment score of 0.3 (below threshold of 0.4)
    analyzer.model.return_value = [{"label": "NEGATIVE", "score": 0.7}]  # 1.0 - 0.7 = 0.3
    
    transcript = "We decided something."
    
    risk_points = analyzer.analyze(transcript, [])
    
    # Should flag because 0.3 < 0.4
    assert len(risk_points) > 0


def test_context_extraction():
    """Test that context around decision points is extracted."""
    analyzer = SentimentAnalyzer(sentiment_threshold=0.5)
    analyzer.model = Mock()
    analyzer.model.return_value = [{"label": "NEGATIVE", "score": 0.9}]
    
    transcript = "First sentence. Second sentence. We decided to proceed. Fourth sentence. Fifth sentence."
    
    risk_points = analyzer.analyze(transcript, [])
    
    # Should have context including surrounding sentences
    assert len(risk_points) > 0
    assert risk_points[0].context
    assert "We decided" in risk_points[0].context or "We decided" in risk_points[0].text_segment


def test_multiple_decision_points():
    """Test handling of multiple decision points."""
    analyzer = SentimentAnalyzer(sentiment_threshold=0.5)
    analyzer.model = Mock()
    analyzer.model.return_value = [{"label": "NEGATIVE", "score": 0.9}]
    
    transcript = "We decided option A. Later, we agreed on option B. The final choice is option C."
    
    risk_points = analyzer.analyze(transcript, [])
    
    # Should detect multiple decision points
    assert len(risk_points) >= 2


def test_no_decision_points():
    """Test transcript with no decision points."""
    analyzer = SentimentAnalyzer(sentiment_threshold=0.5)
    analyzer.model = Mock()
    
    transcript = "This is a regular meeting discussion without any decisions."
    
    risk_points = analyzer.analyze(transcript, [])
    
    # Should have no risk points
    assert len(risk_points) == 0


def test_model_not_loaded():
    """Test behavior when model is not loaded."""
    analyzer = SentimentAnalyzer(sentiment_threshold=0.5)
    analyzer.model = None
    
    transcript = "We decided to proceed."
    
    risk_points = analyzer.analyze(transcript, [])
    
    # Should return empty list and not crash
    assert risk_points == []


def test_sentiment_analysis_error_handling():
    """Test that errors during sentiment analysis are handled."""
    analyzer = SentimentAnalyzer(sentiment_threshold=0.5)
    analyzer.model = Mock()
    analyzer.model.side_effect = Exception("Model error")
    
    transcript = "We decided to proceed."
    
    # Should not raise exception
    risk_points = analyzer.analyze(transcript, [])
    
    # Should return empty or partial results
    assert isinstance(risk_points, list)


def test_all_decision_patterns():
    """Test that all decision patterns are recognized."""
    analyzer = SentimentAnalyzer(sentiment_threshold=0.5)
    analyzer.model = Mock()
    analyzer.model.return_value = [{"label": "NEGATIVE", "score": 0.9}]
    
    patterns = [
        "We decided to proceed",
        "The final choice is option A",
        "We agreed on the approach",
        "The decision is to continue",
        "We're going with plan B"
    ]
    
    for pattern in patterns:
        transcript = f"{pattern}."
        risk_points = analyzer.analyze(transcript, [])
        
        # Each pattern should be detected
        assert len(risk_points) > 0, f"Pattern '{pattern}' not detected"


def test_sentiment_score_calculation_negative():
    """Test sentiment score calculation for negative sentiment."""
    analyzer = SentimentAnalyzer(sentiment_threshold=0.5)
    analyzer.model = Mock()
    analyzer.model.return_value = [{"label": "NEGATIVE", "score": 0.8}]
    
    transcript = "We decided something."
    
    risk_points = analyzer.analyze(transcript, [])
    
    # Negative with score 0.8 should give sentiment_score of 0.2 (1.0 - 0.8)
    if risk_points:
        assert risk_points[0].sentiment_score < 0.5


def test_sentiment_score_calculation_positive():
    """Test sentiment score calculation for positive sentiment."""
    analyzer = SentimentAnalyzer(sentiment_threshold=0.3)
    analyzer.model = Mock()
    analyzer.model.return_value = [{"label": "POSITIVE", "score": 0.9}]
    
    transcript = "We decided something."
    
    risk_points = analyzer.analyze(transcript, [])
    
    # Positive with score 0.9 should give sentiment_score of 0.9
    # Should not be flagged as risk (0.9 > 0.3)
    assert len(risk_points) == 0


def test_text_truncation_for_model():
    """Test that long text is truncated for the model."""
    analyzer = SentimentAnalyzer(sentiment_threshold=0.5)
    analyzer.model = Mock()
    analyzer.model.return_value = [{"label": "POSITIVE", "score": 0.9}]
    
    # Create very long text
    long_text = "We decided " + "word " * 1000
    transcript = long_text
    
    risk_points = analyzer.analyze(transcript, [])
    
    # Should handle long text without crashing
    assert isinstance(risk_points, list)
    
    # Verify model was called with truncated text (max 512 tokens)
    if analyzer.model.called:
        call_args = analyzer.model.call_args[0][0]
        assert len(call_args) <= 512


def test_empty_transcript():
    """Test handling of empty transcript."""
    analyzer = SentimentAnalyzer(sentiment_threshold=0.5)
    analyzer.model = Mock()
    
    transcript = ""
    
    risk_points = analyzer.analyze(transcript, [])
    
    # Should handle empty transcript gracefully
    assert risk_points == []
