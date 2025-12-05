"""Transcript parsing functionality."""

import re
from typing import List
import logging

from .models import SpeakerSegment

logger = logging.getLogger(__name__)


class TranscriptParser:
    """Parser for speaker-identified meeting transcripts."""
    
    # Pattern to match speaker labels: "Speaker Name: text"
    SPEAKER_PATTERN = re.compile(r'^([A-Za-z0-9\s\.]+):\s*(.+)', re.MULTILINE)
    
    def parse(self, transcript_text: str) -> List[SpeakerSegment]:
        """Parse transcript text into speaker segments.
        
        Args:
            transcript_text: Raw transcript text with speaker labels.
            
        Returns:
            List of SpeakerSegment objects.
        """
        if not transcript_text or not transcript_text.strip():
            logger.warning("Empty transcript provided")
            return []
        
        segments = []
        lines = transcript_text.split('\n')
        current_speaker = None
        current_text = []
        current_position = 0
        
        for line in lines:
            match = self.SPEAKER_PATTERN.match(line)
            
            if match:
                # Save previous segment if exists
                if current_speaker is not None:
                    segment_text = '\n'.join(current_text).strip()
                    if segment_text:
                        segments.append(SpeakerSegment(
                            speaker=self._normalize_speaker_name(current_speaker),
                            text=segment_text,
                            start_position=current_position
                        ))
                
                # Start new segment
                current_speaker = match.group(1)
                current_text = [match.group(2)]
                current_position = transcript_text.find(line)
            elif current_speaker is not None:
                # Continue current speaker's text
                current_text.append(line)
        
        # Save final segment
        if current_speaker is not None:
            segment_text = '\n'.join(current_text).strip()
            if segment_text:
                segments.append(SpeakerSegment(
                    speaker=self._normalize_speaker_name(current_speaker),
                    text=segment_text,
                    start_position=current_position
                ))
        
        logger.info(f"Parsed {len(segments)} speaker segments")
        return segments
    
    def _normalize_speaker_name(self, name: str) -> str:
        """Normalize speaker name for consistency.
        
        Args:
            name: Raw speaker name.
            
        Returns:
            Normalized speaker name.
        """
        # Strip whitespace and convert to title case
        normalized = name.strip().title()
        return normalized
