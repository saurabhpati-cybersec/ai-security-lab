"""LLM-as-judge injection classifier.

Uses a small, fast model (claude-haiku-4-5) as judge.
Target latency: <500ms per check.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

from pydantic import BaseModel, ConfigDict

# Lazy import — only if anthropic is available
_ANTHROPIC_AVAILABLE = False
try:
    import anthropic

    _ANTHROPIC_AVAILABLE = True
except ImportError:
    pass


class ClassifierResult(BaseModel):
    model_config = ConfigDict(frozen=True)
    is_injection: bool
    confidence: float
    reasoning: str
    latency_ms: float
    model: str
    error: str | None = None


CLASSIFIER_SYSTEM_PROMPT = (
    Path(__file__).parent.parent / "starter/python/prompt_templates/injection_detection.txt"
)


class ClassifierDetector:
    """LLM-as-judge injection classifier.

    Calibration: threshold=0.7 gives TPR~0.85, FPR~0.05 on reference datasets
    (calibrate yourself using eval_classifier.py in detectors/).
    """

    def __init__(
        self,
        model: str = "claude-haiku-4-5-20251001",
        threshold: float = 0.7,
    ) -> None:
        if not _ANTHROPIC_AVAILABLE:
            raise RuntimeError("anthropic package not installed — pip install anthropic")
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set")
        self._client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.threshold = threshold
        self._system_prompt = CLASSIFIER_SYSTEM_PROMPT.read_text(encoding="utf-8")

    def check(self, text: str) -> ClassifierResult:
        """Classify text as injection or benign using LLM judge."""
        t0 = time.perf_counter()
        try:
            response = self._client.messages.create(
                model=self.model,
                max_tokens=128,
                temperature=0.0,
                system=self._system_prompt,
                messages=[{"role": "user", "content": f"Classify this text:\n\n{text[:2000]}"}],
            )
            raw = response.content[0].text.strip()
            # Extract JSON from response
            json_start = raw.find("{")
            json_end = raw.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                data = json.loads(raw[json_start:json_end])
            else:
                data = json.loads(raw)

            confidence = float(data.get("confidence", 0.5))
            return ClassifierResult(
                is_injection=confidence >= self.threshold,
                confidence=confidence,
                reasoning=data.get("reasoning", ""),
                latency_ms=(time.perf_counter() - t0) * 1000,
                model=self.model,
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            return ClassifierResult(
                is_injection=False,
                confidence=0.0,
                reasoning="",
                latency_ms=(time.perf_counter() - t0) * 1000,
                model=self.model,
                error=f"Parse error: {e}",
            )
        except Exception as e:  # noqa: BLE001 - catch-all for API errors only
            return ClassifierResult(
                is_injection=False,
                confidence=0.0,
                reasoning="",
                latency_ms=(time.perf_counter() - t0) * 1000,
                model=self.model,
                error=f"API error: {e}",
            )
