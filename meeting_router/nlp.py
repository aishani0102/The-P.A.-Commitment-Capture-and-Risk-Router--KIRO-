"""NLP processing for action items and sentiment analysis."""

import re
from typing import List
import logging

from .models import SpeakerSegment, ActionItem, RiskPoint

logger = logging.getLogger(__name__)


class ActionItemExtractor:
    """Extracts action items from transcript segments."""
    
    ACTION_PATTERNS = [
        r"I will\s+(.+)",
        r"I'll\s+(.+)",
        r"Need to\s+(.+)",
        r"Let's follow up on\s+(.+)",
        r"Someone should\s+(.+)",
        r"We need to\s+(.+)",
        r"I can\s+(.+)",
        r"I should\s+(.+)",
    ]
    
    def __init__(self):
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.ACTION_PATTERNS]
    
    def extract(self, segments: List[SpeakerSegment]) -> List[ActionItem]:
        """Extract action items from speaker segments.
        
        Args:
            segments: List of speaker segments to analyze.
            
        Returns:
            List of extracted ActionItem objects.
        """
        action_items = []
        
        for segment in segments:
            items = self._extract_from_segment(segment)
            action_items.extend(items)
        
        logger.info(f"Extracted {len(action_items)} action items")
        return action_items
    
    def _extract_from_segment(self, segment: SpeakerSegment) -> List[ActionItem]:
        """Extract action items from a single segment.
        
        Args:
            segment: Speaker segment to analyze.
            
        Returns:
            List of action items found in this segment.
        """
        items = []
        
        # Split into sentences for better context extraction
        sentences = re.split(r'[.!?]+', segment.text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            for pattern in self.compiled_patterns:
                match = pattern.search(sentence)
                if match:
                    task_description = match.group(1).strip()
                    # Remove trailing punctuation
                    task_description = re.sub(r'[,;]+$', '', task_description)
                    
                    if task_description:
                        items.append(ActionItem(
                            owner=segment.speaker,
                            task_description=task_description,
                            context_quote=sentence
                        ))
        
        return items


class SentimentAnalyzer:
    """Analyzes sentiment to detect risk points in discussions."""
    
    DECISION_PATTERNS = [
        r"We decided",
        r"The final choice is",
        r"We agreed",
        r"The decision is",
        r"We're going with",
        r"We'll go with",
    ]
    
    def __init__(self, sentiment_threshold: float):
        """Initialize sentiment analyzer.
        
        Args:
            sentiment_threshold: Threshold below which to flag risk points (0.0-1.0).
        """
        self.sentiment_threshold = sentiment_threshold
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.DECISION_PATTERNS]
        self.model = None
        self.tokenizer = None
        self._load_model()
    
    def _load_model(self) -> None:
        """Load pre-trained sentiment analysis model."""
        try:
            from transformers import pipeline
            self.model = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
            logger.info("Loaded sentiment analysis model")
        except Exception as e:
            logger.error(f"Failed to load sentiment model: {e}")
            self.model = None
    
    def analyze(self, transcript_text: str, segments: List[SpeakerSegment]) -> List[RiskPoint]:
        """Analyze transcript for risk points based on sentiment.
        
        Args:
            transcript_text: Full transcript text.
            segments: List of speaker segments.
            
        Returns:
            List of identified RiskPoint objects.
        """
        if self.model is None:
            logger.warning("Sentiment model not loaded, skipping sentiment analysis")
            return []
        
        risk_points = []
        
        # Split transcript into sentences
        sentences = re.split(r'[.!?]+', transcript_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Find decision points
        for i, sentence in enumerate(sentences):
            if self._is_decision_point(sentence):
                # Get surrounding context (±2 sentences)
                start_idx = max(0, i - 2)
                end_idx = min(len(sentences), i + 3)
                context_sentences = sentences[start_idx:end_idx]
                context = ' '.join(context_sentences)
                
                # Analyze sentiment
                try:
                    sentiment_score = self._get_sentiment_score(context)
                    
                    if sentiment_score < self.sentiment_threshold:
                        risk_points.append(RiskPoint(
                            text_segment=sentence,
                            sentiment_score=sentiment_score,
                            context=context
                        ))
                        logger.info(f"Risk point detected: {sentence[:50]}... (score: {sentiment_score})")
                except Exception as e:
                    logger.error(f"Sentiment analysis failed for segment: {e}")
                    continue
        
        logger.info(f"Identified {len(risk_points)} risk points")
        return risk_points
    
    def _is_decision_point(self, text: str) -> bool:
        """Check if text contains a decision phrase.
        
        Args:
            text: Text to check.
            
        Returns:
            True if text contains a decision phrase.
        """
        for pattern in self.compiled_patterns:
            if pattern.search(text):
                return True
        return False
    
    def _get_sentiment_score(self, text: str) -> float:
        """Get sentiment score for text.
        
        Args:
            text: Text to analyze.
            
        Returns:
            Sentiment score between 0.0 (negative) and 1.0 (positive).
        """
        result = self.model(text[:512])[0]  # Limit to 512 tokens
        
        # Convert to 0-1 scale where lower is more negative
        if result['label'] == 'NEGATIVE':
            return 1.0 - result['score']
        else:
            return result['score']
