"""Unit tests for summary generator."""

import pytest
from meeting_router.summary import SummaryGenerator
from meeting_router.models import ProcessingResults, ActionItem, CreatedTask, RiskPoint


def test_generate_basic_summary():
    """Test generating a basic summary."""
    results = ProcessingResults(
        action_items=[
            ActionItem("Alice", "Complete the report", "I will complete the report")
        ],
        created_tasks=[
            CreatedTask("TASK-1", "https://example.com/TASK-1", "Complete the report")
        ],
        risk_points=[],
        transcript_text="Meeting discussion about the report."
    )
    
    generator = SummaryGenerator()
    summary = generator.generate(results)
    
    assert "Meeting Summary" in summary
    assert "Alice" in summary
    assert "Complete the report" in summary
    assert "TASK-1" in summary
    assert "https://example.com/TASK-1" in summary


def test_generate_summary_with_risk_points():
    """Test generating summary with risk points."""
    results = ProcessingResults(
        action_items=[],
        created_tasks=[],
        risk_points=[
            RiskPoint(
                text_segment="We decided to proceed",
                sentiment_score=0.25,
                context="There were concerns but we decided to proceed anyway"
            )
        ],
        transcript_text="Meeting discussion."
    )
    
    generator = SummaryGenerator()
    summary = generator.generate(results)
    
    assert "Risk Points" in summary or "🚨" in summary
    assert "0.25" in summary
    assert "We decided to proceed" in summary


def test_generate_summary_no_action_items():
    """Test generating summary with no action items."""
    results = ProcessingResults(
        action_items=[],
        created_tasks=[],
        risk_points=[],
        transcript_text="Meeting discussion with no action items."
    )
    
    generator = SummaryGenerator()
    summary = generator.generate(results)
    
    assert "Meeting Summary" in summary
    assert "Action Items" in summary
    assert "No action items" in summary or "no action items" in summary


def test_generate_summary_multiple_action_items():
    """Test generating summary with multiple action items."""
    results = ProcessingResults(
        action_items=[
            ActionItem("Alice", "Task 1", "Context 1"),
            ActionItem("Bob", "Task 2", "Context 2"),
            ActionItem("Charlie", "Task 3", "Context 3"),
        ],
        created_tasks=[
            CreatedTask("T1", "https://example.com/T1", "Task 1"),
            CreatedTask("T2", "https://example.com/T2", "Task 2"),
            CreatedTask("T3", "https://example.com/T3", "Task 3"),
        ],
        risk_points=[],
        transcript_text="Meeting discussion."
    )
    
    generator = SummaryGenerator()
    summary = generator.generate(results)
    
    # All action items should be present
    assert "Alice" in summary
    assert "Bob" in summary
    assert "Charlie" in summary
    assert "Task 1" in summary
    assert "Task 2" in summary
    assert "Task 3" in summary


def test_markdown_formatting():
    """Test that summary uses proper Markdown formatting."""
    results = ProcessingResults(
        action_items=[
            ActionItem("Alice", "Complete task", "I will complete task")
        ],
        created_tasks=[
            CreatedTask("TASK-1", "https://example.com/TASK-1", "Complete task")
        ],
        risk_points=[],
        transcript_text="Meeting discussion."
    )
    
    generator = SummaryGenerator()
    summary = generator.generate(results)
    
    # Should have Markdown headers
    assert summary.startswith("#")
    assert "##" in summary
    
    # Should have bullet points
    assert "-" in summary or "*" in summary
    
    # Should have Markdown links
    assert "[TASK-1](https://example.com/TASK-1)" in summary


def test_key_decisions_extraction():
    """Test extraction of key decisions from transcript."""
    results = ProcessingResults(
        action_items=[],
        created_tasks=[],
        risk_points=[],
        transcript_text="We decided to use PostgreSQL. The final choice is React for the frontend."
    )
    
    generator = SummaryGenerator()
    summary = generator.generate(results)
    
    # Should extract key decisions
    assert "Key Decisions" in summary
    # Should contain decision content
    assert "PostgreSQL" in summary or "React" in summary


def test_context_quotes_included():
    """Test that context quotes are included."""
    results = ProcessingResults(
        action_items=[
            ActionItem("Alice", "Task", "I will complete this task by Friday")
        ],
        created_tasks=[
            CreatedTask("T1", "https://example.com/T1", "Task")
        ],
        risk_points=[],
        transcript_text="Meeting discussion."
    )
    
    generator = SummaryGenerator()
    summary = generator.generate(results)
    
    # Context quote should be in summary
    assert "I will complete this task by Friday" in summary
    assert "Context:" in summary


def test_risk_points_formatting():
    """Test formatting of risk points section."""
    results = ProcessingResults(
        action_items=[],
        created_tasks=[],
        risk_points=[
            RiskPoint("Decision text", 0.15, "Full context here"),
            RiskPoint("Another decision", 0.28, "More context"),
        ],
        transcript_text="Meeting discussion."
    )
    
    generator = SummaryGenerator()
    summary = generator.generate(results)
    
    # Should have risk points section
    assert "🚨" in summary or "Risk Points" in summary
    
    # Should show sentiment scores
    assert "0.15" in summary
    assert "0.28" in summary
    
    # Should show decision text
    assert "Decision text" in summary
    assert "Another decision" in summary


def test_timestamp_in_header():
    """Test that timestamp is included in header."""
    results = ProcessingResults(
        action_items=[],
        created_tasks=[],
        risk_points=[],
        transcript_text="Meeting discussion."
    )
    
    generator = SummaryGenerator()
    summary = generator.generate(results)
    
    # Should have timestamp in header
    assert "Meeting Summary -" in summary
    # Should have date/time components
    lines = summary.split('\n')
    header = lines[0]
    assert any(char.isdigit() for char in header)


def test_owner_bold_formatting():
    """Test that owners are formatted in bold."""
    results = ProcessingResults(
        action_items=[
            ActionItem("Alice", "Task", "Context")
        ],
        created_tasks=[
            CreatedTask("T1", "https://example.com/T1", "Task")
        ],
        risk_points=[],
        transcript_text="Meeting discussion."
    )
    
    generator = SummaryGenerator()
    summary = generator.generate(results)
    
    # Owner should be in bold (Markdown: **Alice**)
    assert "**Alice**" in summary


def test_no_risk_section_when_empty():
    """Test that risk section is not included when no risks."""
    results = ProcessingResults(
        action_items=[
            ActionItem("Alice", "Task", "Context")
        ],
        created_tasks=[
            CreatedTask("T1", "https://example.com/T1", "Task")
        ],
        risk_points=[],
        transcript_text="Meeting discussion."
    )
    
    generator = SummaryGenerator()
    summary = generator.generate(results)
    
    # Should not have prominent risk section
    # (May have the header but no content)
    lines = summary.split('\n')
    risk_section_lines = [i for i, line in enumerate(lines) if "Risk Points" in line or "🚨" in line]
    
    # If risk section exists, it should be minimal
    if risk_section_lines:
        # Check that there's not much content after it
        risk_line_idx = risk_section_lines[0]
        remaining_lines = lines[risk_line_idx + 1:]
        # Should have very few lines after risk section header
        assert len([l for l in remaining_lines if l.strip()]) < 3


def test_multiple_risk_points():
    """Test handling of multiple risk points."""
    results = ProcessingResults(
        action_items=[],
        created_tasks=[],
        risk_points=[
            RiskPoint("Risk 1", 0.1, "Context 1"),
            RiskPoint("Risk 2", 0.2, "Context 2"),
            RiskPoint("Risk 3", 0.3, "Context 3"),
        ],
        transcript_text="Meeting discussion."
    )
    
    generator = SummaryGenerator()
    summary = generator.generate(results)
    
    # All risk points should be present
    assert "Risk 1" in summary
    assert "Risk 2" in summary
    assert "Risk 3" in summary
    assert "0.1" in summary or "0.10" in summary
    assert "0.2" in summary or "0.20" in summary
    assert "0.3" in summary or "0.30" in summary


def test_empty_transcript():
    """Test handling of empty transcript."""
    results = ProcessingResults(
        action_items=[],
        created_tasks=[],
        risk_points=[],
        transcript_text=""
    )
    
    generator = SummaryGenerator()
    summary = generator.generate(results)
    
    # Should still generate valid summary
    assert summary
    assert "Meeting Summary" in summary
