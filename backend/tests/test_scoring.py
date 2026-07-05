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


def test_calculate_score_new_owasp_categories():
    results = {
        "system_prompt_extraction": [True] * 5,
        "tool_output_injection": [False] * 5,
        "prompt_boundary_probing": [True] * 5,
        "tool_loop_exploit": [False] * 5,
    }
    score, breakdown = calculate_score(results)
    assert "LLM02: Sensitive Information Disclosure" in breakdown
    assert "LLM05: Improper Output Handling" in breakdown
    assert "LLM07: System Prompt Leakage" in breakdown
    assert "LLM10: Unbounded Consumption" in breakdown
    assert score == 50.0


def test_calculate_score_all_13_scenarios():
    results = {
        "goal_deviation": [True] * 5,
        "excessive_agency": [True] * 5,
        "indirect_injection": [True] * 5,
        "permission_boundary": [True] * 5,
        "multi_step_chain": [True] * 5,
        "role_play_jailbreak": [True] * 5,
        "token_smuggling": [True] * 5,
        "context_window_overflow": [True] * 5,
        "tool_abuse": [True] * 5,
        "system_prompt_extraction": [True] * 5,
        "tool_output_injection": [True] * 5,
        "prompt_boundary_probing": [True] * 5,
        "tool_loop_exploit": [True] * 5,
    }
    score, breakdown = calculate_score(results)
    assert score == 100.0
    assert len(breakdown) == 6
