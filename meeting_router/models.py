"""Data models for Meeting Router."""

from dataclasses import dataclass
from typing import List


@dataclass
class SpeakerSegment:
    """A segment of transcript attributed to a specific speaker."""
    speaker: str
    text: str
    start_position: int


@dataclass
class ActionItem:
    """An action item extracted from the transcript."""
    owner: str
    task_description: str
    context_quote: str


@dataclass
class RiskPoint:
    """A risk point identified through sentiment analysis."""
    text_segment: str
    sentiment_score: float
    context: str


@dataclass
class CreatedTask:
    """A task that has been created in a backend system."""
    task_id: str
    url: str
    title: str


@dataclass
class ProcessingResults:
    """Results from processing a transcript."""
    action_items: List[ActionItem]
    created_tasks: List[CreatedTask]
    risk_points: List[RiskPoint]
    transcript_text: str
