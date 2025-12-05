"""Summary generation for meeting processing results."""

import logging
from datetime import datetime
from typing import List

from .models import ProcessingResults, ActionItem, CreatedTask, RiskPoint

logger = logging.getLogger(__name__)


class SummaryGenerator:
    """Generates formatted summary digests from processing results."""
    
    def generate(self, results: ProcessingResults) -> str:
        """Generate a Markdown summary digest.
        
        Args:
            results: Processing results to summarize.
            
        Returns:
            Markdown-formatted summary string.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        sections = []
        
        # Header
        sections.append(f"# Meeting Summary - {timestamp}\n")
        
        # Key Decisions section
        decisions = self._extract_key_decisions(results)
        if decisions:
            sections.append("## Key Decisions\n")
            for decision in decisions:
                sections.append(f"- {decision}\n")
            sections.append("\n")
        
        # Action Items section
        if results.action_items:
            sections.append("## Action Items\n")
            for i, (action_item, task) in enumerate(zip(results.action_items, results.created_tasks)):
                sections.append(f"- **{action_item.owner}**: {action_item.task_description}\n")
                sections.append(f"  - [{task.task_id}]({task.url})\n")
                sections.append(f"  - Context: \"{action_item.context_quote}\"\n\n")
        else:
            sections.append("## Action Items\n")
            sections.append("No action items were identified in this meeting.\n\n")
        
        # Risk Points section (conditional)
        if results.risk_points:
            sections.append("## 🚨 Risk Points for Review\n")
            for risk in results.risk_points:
                sections.append(f"- **Sentiment Score: {risk.sentiment_score:.2f}**\n")
                sections.append(f"  - \"{risk.text_segment}\"\n")
                sections.append(f"  - Context: {risk.context}\n\n")
        
        summary = "".join(sections)
        logger.info("Generated summary digest")
        return summary
    
    def _extract_key_decisions(self, results: ProcessingResults) -> List[str]:
        """Extract key decisions from non-action-item text.
        
        Args:
            results: Processing results.
            
        Returns:
            List of key decision statements.
        """
        import re
        
        decisions = []
        decision_patterns = [
            r"[Ww]e decided (.+?)[\.\n]",
            r"[Tt]he final choice is (.+?)[\.\n]",
            r"[Ww]e agreed (.+?)[\.\n]",
            r"[Tt]he decision is (.+?)[\.\n]",
            r"[Ww]e're going with (.+?)[\.\n]",
        ]
        
        for pattern in decision_patterns:
            matches = re.findall(pattern, results.transcript_text)
            for match in matches:
                decision = match.strip()
                if decision and decision not in decisions:
                    decisions.append(decision)
        
        return decisions
