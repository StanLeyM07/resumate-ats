"""Tests for the model-response parser.

The parser is the component most likely to fail in production: the system
prompt tells the model to return bare JSON, and models comply most of the
time rather than all of the time. Each case below is a response shape that
was either observed or is cheap to defend against.
"""

import json
import pytest

from backend.scorer import parse_model_json

VALID = {
    "candidate_name": "Ivy Chen",
    "match_score": 85,
    "verdict": "Strong Match",
    "extracted_skills": ["FastAPI", "Python"],
    "years_experience": 1.5,
    "key_strengths": ["Proven FastAPI experience"],
    "concerns": ["Limited years"],
}
BODY = json.dumps(VALID)


def test_bare_json():
    assert parse_model_json(BODY) == VALID


def test_json_fence():
    assert parse_model_json(f"```json\n{BODY}\n```") == VALID


def test_uppercase_fence():
    """The original implementation only matched a lowercase ```json."""
    assert parse_model_json(f"```JSON\n{BODY}\n```") == VALID


def test_bare_fence():
    assert parse_model_json(f"```\n{BODY}\n```") == VALID


def test_prose_around_fence():
    """The original stripped fences only at the very start and end, so any
    leading sentence left the fence embedded and json.loads failed."""
    noisy = f"Sure, here is the analysis:\n\n```json\n{BODY}\n```\n\nLet me know."
    assert parse_model_json(noisy) == VALID


def test_prose_without_fence():
    assert parse_model_json(f"Here you go: {BODY} -- hope that helps") == VALID


def test_unterminated_fence():
    """Truncated output: an opening fence with no closing one."""
    assert parse_model_json(f"```json\n{BODY}") == VALID


def test_whitespace_tolerated():
    assert parse_model_json(f"\n\n  {BODY}  \n\n") == VALID


def test_none_raises_value_error():
    """`choices[0].message.content` is Optional; the old code called .strip()
    on it and raised an opaque AttributeError."""
    with pytest.raises(ValueError):
        parse_model_json(None)


def test_empty_raises_value_error():
    with pytest.raises(ValueError):
        parse_model_json("   ")


def test_malformed_json_raises():
    with pytest.raises(json.JSONDecodeError):
        parse_model_json("{ not valid json ")
