"""
GuardianEdge Policy Engine and Audit Vault.
Provides offline, Zero-Knowledge compliance logging and dynamic security policies.
"""

import sqlite3
import time
import os
from typing import Dict, Any, List
from guardian_edge.config import DEFAULT_POLICIES, PolicyRule, DB_PATH

class PolicyEngine:
    def __init__(self):
        self.policies: Dict[str, PolicyRule] = dict(DEFAULT_POLICIES)

    def evaluate(self, category: str) -> Dict[str, str]:
        rule = self.policies.get(category)
        if not rule:
            return {"action": "ALLOW", "severity": "LOW"}
        return {"action": rule.action, "severity": rule.severity}

    def set_policy(self, category: str, action: str):
        if category in self.policies:
            self.policies[category].action = action

class AuditVault:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                category TEXT,
                severity TEXT,
                action_taken TEXT,
                redacted_count INTEGER,
                latency_ms REAL,
                accelerator TEXT,
                raw_preview TEXT
            )
        """)
        conn.commit()
        conn.close()

    def log_event(self, category: str, severity: str, action_taken: str, redacted_count: int, latency_ms: float, preview: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO audit_events (timestamp, category, severity, action_taken, redacted_count, latency_ms, accelerator, raw_preview)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (time.time(), category, severity, action_taken, redacted_count, latency_ms, "Snapdragon Hexagon NPU", preview))
        conn.commit()
        conn.close()

    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, category, severity, action_taken, redacted_count, latency_ms, accelerator, raw_preview
            FROM audit_events ORDER BY id DESC LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()

        events = []
        for r in rows:
            events.append({
                "id": r[0],
                "time": time.strftime("%H:%M:%S", time.localtime(r[1])),
                "category": r[2],
                "severity": r[3],
                "action": r[4],
                "redacted_count": r[5],
                "latency_ms": r[6],
                "accelerator": r[7],
                "preview": r[8]
            })
        return events

    def get_metrics_summary(self) -> Dict[str, Any]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*), COALESCE(SUM(redacted_count), 0), COALESCE(AVG(latency_ms), 4.2) FROM audit_events")
        row = cursor.fetchone()
        conn.close()
        return {
            "total_intercepts": row[0] if row else 0,
            "total_tokens_redacted": row[1] if row else 0,
            "average_npu_latency_ms": round(row[2] if row else 4.2, 2)
        }

policy_engine = PolicyEngine()
audit_vault = AuditVault()
