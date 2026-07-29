import pytest
from logs.log_analytics_engine import AnalyticsLogEngine, analytics_engine

def test_analytics_log_engine_initial_empty():
    engine = AnalyticsLogEngine()
    metrics = engine.get_summary_metrics()
    assert metrics["total_tickets"] == 0
    assert metrics["ai_resolution_rate"] == "100%"
    assert metrics["escalation_rate"] == "0%"

def test_analytics_log_engine_metrics_calculation():
    engine = AnalyticsLogEngine()
    engine.log_ticket_metrics(
        ticket_id=1,
        intent="ORDER_INQUIRY",
        resolution_time_sec=12.5,
        escalated=False,
        sentiment="POSITIVE"
    )
    engine.log_ticket_metrics(
        ticket_id=2,
        intent="PAYMENT_ISSUE",
        resolution_time_sec=25.0,
        escalated=True,
        sentiment="VERY_NEGATIVE"
    )
    
    metrics = engine.get_summary_metrics()
    assert metrics["total_tickets"] == 2
    assert metrics["ai_resolution_rate"] == "50.0%"
    assert metrics["escalation_rate"] == "50.0%"
    assert metrics["avg_resolution_time_sec"] == 18.75
