"""Unit tests for GuardianEdge DLP detector and redactor."""

import pytest
from guardian_edge.detector import detector
from guardian_edge.redactor import redactor
from guardian_edge.npu_engine import npu_engine

def test_api_key_detection():
    sample = "My key is sk-proj-1234567890abcdefABCDEF1234567890"
    entities, telemetry = detector.scan_text(sample)
    assert len(entities) >= 1
    assert entities[0].category == "API_KEYS"
    assert entities[0].severity == "CRITICAL"
    assert telemetry["latency_ms"] > 0

def test_credit_card_luhn_detection():
    # Valid test Visa number (Luhn compliant)
    sample = "Pay with 4242424242424242"
    entities, _ = detector.scan_text(sample)
    assert any(e.category == "PII_FINANCIAL" for e in entities)

def test_redaction_pipeline():
    sample = "AWS key is AKIAIOSFODNN7EXAMPLE and token is ghp_1234567890abcdef1234567890abcdef1234"
    entities, _ = detector.scan_text(sample)
    redacted, count = redactor.redact_text(sample, entities)
    assert count >= 2
    assert "AKIAIOSFODNN7EXAMPLE" not in redacted
    assert "[REDACTED_API_KEYS]" in redacted

def test_npu_telemetry():
    status = npu_engine.get_hardware_telemetry()
    assert "Snapdragon" in status["device"]
    assert status["npu_peak_tops"] == 45.0
    assert status["energy_efficiency_multiplier"] > 50
