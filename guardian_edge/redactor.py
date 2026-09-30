"""
GuardianEdge Active Redaction Engine.
Performs zero-latency token substitution, synthetic replacement, and privacy-preserving masking.
"""

from typing import List, Tuple
from guardian_edge.detector import SensitiveEntity

class Redactor:
    @staticmethod
    def redact_text(text: str, entities: List[SensitiveEntity], mask_style: str = "SYNTHETIC_LABEL") -> Tuple[str, int]:
        """
        Replace detected sensitive entities in reverse order of index to maintain offset integrity.
        mask_style options:
          - "SYNTHETIC_LABEL": e.g. [REDACTED_API_KEY_1]
          - "ASTERISK": e.g. ********************
          - "SAFE_MOCK": e.g. "sk-proj-DEMO-TEST-KEY-0000"
        """
        if not entities:
            return text, 0

        # Sort entities by start index in descending order
        sorted_entities = sorted(entities, key=lambda e: e.start, reverse=True)
        
        # Remove overlaps
        non_overlapping = []
        last_start = len(text) + 1
        for e in sorted_entities:
            if e.end <= last_start:
                non_overlapping.append(e)
                last_start = e.start

        redacted_count = len(non_overlapping)
        result = list(text)

        for i, e in enumerate(non_overlapping):
            if mask_style == "SYNTHETIC_LABEL":
                replacement = f"[REDACTED_{e.category}]"
            elif mask_style == "ASTERISK":
                replacement = "*" * len(e.value)
            elif mask_style == "SAFE_MOCK":
                if e.category == "API_KEYS":
                    replacement = "sk-proj-MOCK_KEY_SNAPDRAGON_NPU_PROTECTED"
                elif e.category == "PII_FINANCIAL":
                    replacement = "4111-XXXX-XXXX-1111"
                elif e.category == "PII_NATIONAL_ID":
                    replacement = "XXXX-XXXX-1234"
                else:
                    replacement = f"[SAFE_TOKEN_{e.category}]"
            else:
                replacement = f"[PROTECTED_{e.category}]"

            result[e.start:e.end] = list(replacement)

        return "".join(result), redacted_count

redactor = Redactor()
