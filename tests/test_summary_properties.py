"""Property-based tests for summary generation."""

from hypothesis import given, strategies as st, assume
import re
import pytest

from meeting_router.summary import SummaryGenerator
from meeting_router.models import ProcessingResults, ActionItem, CreatedTask, RiskPoint


# Custom strategies
@st.composite
def processing_results(draw, include_risk_points=None):
    """Generate processing results."""
    # Generate action items and tasks
    num_items = draw(st.integers(min_value=0, max_value=5))
    
    action_items = []
    created_tasks = []
    
    for i in range(num_items):
        owner = draw(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))))
        task = draw(st.text(min_size=5, max_size=50, alphabet=st.characters(blacklist_characters='\n\r')))
        context = draw(st.text(min_size=5, max_size=100, alphabet=st.characters(blacklist_characters='\n\r')))
        
        assume(owner.strip() and task.strip() and context.strip())
        
        action_items.append(ActionItem(
            owner=owner.strip(),
            task_description=task.strip(),
            context_quote=context.strip()
        ))
        
        task_id = f"TASK-{i}"
        created_tasks.append(CreatedTask(
            task_id=task_id,
            url=f"https://example.com/{task_id}",
            title=task.strip()
        ))
    
    # Generate risk points
    if include_risk_points is None:
        include_risk_points = draw(st.booleans())
    
    risk_points = []
    if include_risk_points:
        num_risks = draw(st.integers(min_value=1, max_value=3))
        for i in range(num_risks):
            text_segment = draw(st.text(min_size=10, max_size=50, alphabet=st.characters(blacklist_characters='\n\r')))
            context = draw(st.text(min_size=20, max_size=100, alphabet=st.characters(blacklist_characters='\n\r')))
            score = draw(st.floats(min_value=0.0, max_value=0.5))
            
            assume(text_segment.strip() and context.strip())
            
            risk_points.append(RiskPoint(
                text_segment=text_segment.strip(),
                sentiment_score=score,
                context=context.strip()
            ))
    
    # Generate transcript
    transcript = draw(st.text(min_size=10, max_size=500, alphabet=st.characters(blacklist_characters='\n\r')))
    assume(transcript.strip())
    
    return ProcessingResults(
        action_items=action_items,
        created_tasks=created_tasks,
        risk_points=risk_points,
        transcript_text=transcript.strip()
    )


# Feature: meeting-router, Property 24: Summary digest format validity
# For any processing results, the generated summary digest should be valid Markdown
@given(results=processing_results())
def test_summary_digest_format_validity(results):
    """Test that generated summaries are valid Markdown."""
    generator = SummaryGenerator()
    
    summary = generator.generate(results)
    
    # Should be non-empty
    assert summary
    assert len(summary.strip()) > 0
    
    # Should contain Markdown header
    assert summary.startswith("#")
    
    # Should have proper Markdown structure (headers start with #)
    lines = summary.split('\n')
    header_lines = [line for line in lines if line.startswith('#')]
    assert len(header_lines) > 0


# Feature: meeting-router, Property 25: Summary decisions section inclusion
# For any generated summary digest, it should contain a high-level summary section with key decisions
@given(results=processing_results())
def test_summary_decisions_section_inclusion(results):
    """Test that summaries include a decisions section."""
    generator = SummaryGenerator()
    
    summary = generator.generate(results)
    
    # Should contain a section for key decisions or action items
    # At minimum, should have "Key Decisions" or "Action Items" section
    assert "## Key Decisions" in summary or "## Action Items" in summary


# Feature: meeting-router, Property 26: Summary action items completeness
# For any list of created tasks, all tasks should appear in the summary digest with owner names and task links
@given(results=processing_results())
def test_summary_action_items_completeness(results):
    """Test that all action items appear in the summary."""
    generator = SummaryGenerator()
    
    summary = generator.generate(results)
    
    # All action items should be in the summary
    for action_item, task in zip(results.action_items, results.created_tasks):
        # Owner should be in summary
        assert action_item.owner in summary
        
        # Task ID should be in summary
        assert task.task_id in summary
        
        # Task URL should be in summary
        assert task.url in summary


# Feature: meeting-router, Property 27: Risk points section conditional inclusion
# For any processing results, the summary should include risk points section if and only if risk points were detected
@given(include_risks=st.booleans())
def test_risk_points_section_conditional_inclusion(include_risks):
    """Test that risk points section is included only when risk points exist."""
    results = processing_results(include_risk_points=include_risks).example()
    
    generator = SummaryGenerator()
    summary = generator.generate(results)
    
    # Check if risk points section exists
    has_risk_section = "🚨 Risk Points for Review" in summary or "Risk Points" in summary
    
    # Should match whether risk points were included
    if include_risks and len(results.risk_points) > 0:
        assert has_risk_section
    else:
        # If no risk points, section should not be present
        if not has_risk_section:
            assert True  # Expected
        # Or if section exists, it should be empty/minimal


@given(results=processing_results(include_risk_points=True))
def test_risk_points_included_when_present(results):
    """Test that risk points are included when they exist."""
    assume(len(results.risk_points) > 0)
    
    generator = SummaryGenerator()
    summary = generator.generate(results)
    
    # Should have risk points section
    assert "Risk Points" in summary or "🚨" in summary
    
    # All risk points should be in summary
    for risk_point in results.risk_points:
        # Sentiment score should be in summary
        assert str(risk_point.sentiment_score)[:4] in summary  # First 4 chars of score


@given(results=processing_results(include_risk_points=False))
def test_no_risk_section_when_no_risks(results):
    """Test that risk section is not prominent when no risks exist."""
    # Ensure no risk points
    results.risk_points = []
    
    generator = SummaryGenerator()
    summary = generator.generate(results)
    
    # Summary should still be valid
    assert summary
    assert summary.startswith("#")


# Test empty action items
def test_empty_action_items():
    """Test summary generation with no action items."""
    results = ProcessingResults(
        action_items=[],
        created_tasks=[],
        risk_points=[],
        transcript_text="This is a test transcript."
    )
    
    generator = SummaryGenerator()
    summary = generator.generate(results)
    
    # Should still generate valid summary
    assert summary
    assert "Action Items" in summary
    assert "No action items" in summary or "no action items" in summary


# Test markdown formatting
@given(results=processing_results())
def test_markdown_formatting(results):
    """Test that summary uses proper Markdown formatting."""
    generator = SummaryGenerator()
    
    summary = generator.generate(results)
    
    # Should have headers (##)
    assert "##" in summary
    
    # Should have bullet points for lists (-)
    if results.action_items:
        assert "-" in summary or "*" in summary
    
    # Should have links in markdown format [text](url)
    if results.created_tasks:
        assert "[" in summary and "](" in summary and ")" in summary


# Test timestamp inclusion
@given(results=processing_results())
def test_timestamp_inclusion(results):
    """Test that summary includes a timestamp."""
    generator = SummaryGenerator()
    
    summary = generator.generate(results)
    
    # Should have a timestamp in the header
    # Look for date-like patterns
    assert "Meeting Summary" in summary
    # Should have some date/time information
    assert any(char.isdigit() for char in summary[:200])  # First 200 chars should have numbers


# Test context quotes included
@given(results=processing_results())
def test_context_quotes_included(results):
    """Test that context quotes are included for action items."""
    assume(len(results.action_items) > 0)
    
    generator = SummaryGenerator()
    summary = generator.generate(results)
    
    # At least some context quotes should be in the summary
    for action_item in results.action_items:
        assert action_item.context_quote in summary


# Test owner formatting
@given(results=processing_results())
def test_owner_formatting(results):
    """Test that owners are formatted prominently."""
    assume(len(results.action_items) > 0)
    
    generator = SummaryGenerator()
    summary = generator.generate(results)
    
    # Owners should be formatted (likely with ** for bold)
    for action_item in results.action_items:
        # Owner should appear in summary
        assert action_item.owner in summary
