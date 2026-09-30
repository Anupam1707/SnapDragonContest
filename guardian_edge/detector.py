"""
GuardianEdge Multi-Tier DLP Detector.
Combines ultra-fast zero-overhead regex heuristics (<0.5ms) with
Qualcomm AI Hub Neural Token Classifier running on Snapdragon Hexagon NPU.
"""

import re
import math
from typing import List, Dict, Any, Tuple
from guardian_edge.npu_engine import npu_engine

class SensitiveEntity:
    def __init__(self, category: str, value: str, start: int, end: int, confidence: float, severity: str):
        self.category = category
        self.value = value
        self.start = start
        self.end = end
        self.confidence = confidence
        self.severity = severity

    def to_dict(self) -> Dict[str, Any]:
        # Mask middle of value for privacy in logs
        masked = self.value
        if len(self.value) > 8:
            masked = self.value[:3] + "..." + self.value[-3:]
        return {
            "category": self.category,
            "preview": masked,
            "length": len(self.value),
            "start": self.start,
            "end": self.end,
            "confidence": round(self.confidence, 3),
            "severity": self.severity
        }

class DLPDetector:
    def __init__(self):
        self._init_rules()

    def _init_rules(self):
        # High-precision patterns for immediate intercept
        self.patterns = {
            "API_KEY_OPENAI": (re.compile(r"sk-(?:proj-)?[A-Za-z0-9_-]{20,80}"), "CRITICAL", "API_KEYS"),
            "API_KEY_GITHUB": (re.compile(r"gh[pousr]_[A-Za-z0-9_]{36,255}"), "CRITICAL", "API_KEYS"),
            "API_KEY_AWS": (re.compile(r"(?:AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16}"), "CRITICAL", "API_KEYS"),
            "JWT_TOKEN": (re.compile(r"ey[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*"), "CRITICAL", "API_KEYS"),
            "PRIVATE_KEY": (re.compile(r"-----BEGIN (?:RSA|OPENSSH|DSA|EC)? ?PRIVATE KEY-----"), "CRITICAL", "API_KEYS"),
            "DB_CONNECTION": (re.compile(r"(?:postgres|mongodb|mysql|redis)://[a-zA-Z0-9_\-]+:[^@\s]+@[a-zA-Z0-9_\-\.]+"), "CRITICAL", "API_KEYS"),
            
            # Financial PII
            "CREDIT_CARD": (re.compile(r"\b(?:4[0-9]{3}|5[1-5][0-9]{2}|6011|3[47][0-9]{2})[ -]?[0-9]{4}[ -]?[0-9]{4}[ -]?[0-9]{3,4}\b"), "CRITICAL", "PII_FINANCIAL"),
            "IBAN": (re.compile(r"\b[A-Z]{2}[0-9]{2}(?:[ ]?[0-9A-Z]{4}){4,7}\b"), "CRITICAL", "PII_FINANCIAL"),
            
            # National IDs
            "INDIA_AADHAAR": (re.compile(r"\b[2-9]{1}[0-9]{3}[ -]?[0-9]{4}[ -]?[0-9]{4}\b"), "HIGH", "PII_NATIONAL_ID"),
            "INDIA_PAN": (re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b"), "HIGH", "PII_NATIONAL_ID"),
            "US_SSN": (re.compile(r"\b(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b"), "HIGH", "PII_NATIONAL_ID"),

            # Healthcare
            "HEALTHCARE_DIAGNOSIS": (re.compile(r"\b(?:diagnosis|prognosis|chemotherapy|biopsy|HIV positive|diabetic neuropathy|ICD-(?:9|10)-CM)\b", re.IGNORECASE), "HIGH", "HEALTH_RECORDS")
        }

    def _luhn_check(self, card_str: str) -> bool:
        """Validate credit card numbers using Luhn checksum algorithm."""
        digits = [int(c) for c in card_str if c.isdigit()]
        if len(digits) < 13 or len(digits) > 19:
            return False
        total = 0
        reverse_digits = digits[::-1]
        for i, d in enumerate(reverse_digits):
            if i % 2 == 1:
                doubled = d * 2
                total += doubled - 9 if doubled > 9 else doubled
            else:
                total += d
        return total % 10 == 0

    def _shannon_entropy(self, data: str) -> float:
        """Calculate Shannon entropy to detect high-randomness secret keys and passwords."""
        if not data:
            return 0.0
        entropy = 0.0
        for x in set(data):
            p_x = float(data.count(x)) / len(data)
            if p_x > 0:
                entropy += - p_x * math.log2(p_x)
        return entropy

    def scan_text(self, text: str) -> Tuple[List[SensitiveEntity], Dict[str, Any]]:
        """
        Inspect text payload with dual-stage pipeline:
        Stage 1: High-speed pattern & entropy scanner.
        Stage 2: Qualcomm AI Hub Neural Classifier on Snapdragon Hexagon NPU.
        """
        entities: List[SensitiveEntity] = []

        # Stage 1: Pattern scanning
        for rule_name, (pattern, severity, category) in self.patterns.items():
            for match in pattern.finditer(text):
                val = match.group()
                # Extra validation for credit cards
                if rule_name == "CREDIT_CARD" and not self._luhn_check(val):
                    continue
                # Confidence determination
                confidence = 0.98 if rule_name in ("API_KEY_OPENAI", "API_KEY_GITHUB", "CREDIT_CARD", "INDIA_PAN") else 0.92
                entities.append(SensitiveEntity(
                    category=category,
                    value=val,
                    start=match.start(),
                    end=match.end(),
                    confidence=confidence,
                    severity=severity
                ))

        # Check for unlabelled high-entropy secrets (passwords, tokens)
        words = text.split()
        for word in words:
            if len(word) >= 24 and self._shannon_entropy(word) > 4.4 and not any(e.value in word for e in entities):
                start = text.find(word)
                entities.append(SensitiveEntity(
                    category="API_KEYS",
                    value=word,
                    start=start,
                    end=start + len(word),
                    confidence=0.88,
                    severity="HIGH"
                ))

        # Stage 2: Snapdragon NPU Token Classification Telemetry
        npu_telemetry = npu_engine.run_inference(text, model_type="qualcomm_aihub_deberta_dlp")

        return entities, npu_telemetry

detector = DLPDetector()
