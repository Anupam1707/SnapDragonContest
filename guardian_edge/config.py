"""
GuardianEdge Configuration and Runtime Profiles.
Designed for Snapdragon® X Elite & X Plus (HP OmniBook) platforms.
"""

from dataclasses import dataclass, field
from typing import List, Dict
import os

@dataclass
class NPUConfig:
    target_hardware: str = "Snapdragon X Elite (Hexagon NPU)"
    npu_tops: float = 45.0
    execution_provider: str = "QNNExecutionProvider"  # Qualcomm AI Engine Direct
    precision: str = "INT8 / FP16"
    chipset_family: str = "Snapdragon X Series"
    typical_latency_ms: float = 4.2
    idle_power_watts: float = 0.08
    active_power_watts: float = 0.22
    cpu_active_power_watts: float = 18.5  # Baseline comparison for CPU inference

@dataclass
class PolicyRule:
    category: str
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    action: str    # "AUTO_REDACT", "BLOCK", "WARN", "ALLOW"
    description: str
    patterns: List[str] = field(default_factory=list)

DEFAULT_POLICIES: Dict[str, PolicyRule] = {
    "API_KEYS": PolicyRule(
        category="API_KEYS",
        severity="CRITICAL",
        action="AUTO_REDACT",
        description="Cloud provider keys, OpenAI/Anthropic keys, GitHub tokens, JWT tokens, AWS Secret Keys",
    ),
    "PII_FINANCIAL": PolicyRule(
        category="PII_FINANCIAL",
        severity="CRITICAL",
        action="AUTO_REDACT",
        description="Credit Card numbers, Bank Account numbers, CVVs, IBANs",
    ),
    "PII_NATIONAL_ID": PolicyRule(
        category="PII_NATIONAL_ID",
        severity="HIGH",
        action="AUTO_REDACT",
        description="Indian Aadhaar, PAN Cards, US SSN, Passports",
    ),
    "HEALTH_RECORDS": PolicyRule(
        category="HEALTH_RECORDS",
        severity="HIGH",
        action="WARN",
        description="Patient IDs, medical conditions, ICD-10 diagnostic codes",
    ),
    "PROPRIETARY_CODE": PolicyRule(
        category="PROPRIETARY_CODE",
        severity="MEDIUM",
        action="WARN",
        description="Internal source code snippets, database connection strings, SSH private keys",
    )
}

DB_PATH = os.path.expanduser("~/.guardian_edge_vault.db")
PORT = 8844
HOST = "127.0.0.1"
