from app.scoring.calculator import calculate_score


def test_calculate_score_all_pass():
    results = {
        "goal_deviation": [True] * 5,
        "excessive_agency": [True] * 5,
    }
    score, breakdown = calculate_score(results)
    assert score == 100.0


def test_calculate_score_all_fail():
    results = {
        "goal_deviation": [False] * 5,
        "excessive_agency": [False] * 5,
    }
    score, breakdown = calculate_score(results)
    assert score == 0.0


def test_calculate_score_mixed():
    results = {
        "goal_deviation": [True, True, False, False, True],
        "excessive_agency": [True, True, True, False, False],
    }
    score, breakdown = calculate_score(results)
    assert score > 0 and score < 100


def test_calculate_score_empty():
    results = {}
    score, breakdown = calculate_score(results)
    assert score == 0.0
    assert breakdown == {}


def test_calculate_score_owasp_breakdown():
    results = {
        "goal_deviation": [True] * 5,
        "excessive_agency": [False] * 5,
    }
    score, breakdown = calculate_score(results)
    assert "LLM01: Prompt Injection" in breakdown
    assert "LLM06: Excessive Agency" in breakdown
