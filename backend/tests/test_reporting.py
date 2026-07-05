import json
import io

import pytest

from app.reporting.vulnerability_data import SCENARIO_METADATA
from app.scoring.calculator import SCENARIO_OWASP_MAP


def test_vulnerability_data_has_all_scenarios():
    assert len(SCENARIO_METADATA) == 13
    for sname in SCENARIO_OWASP_MAP:
        assert sname in SCENARIO_METADATA, f"Missing metadata for {sname}"


def test_vulnerability_data_fields():
    for sname, meta in SCENARIO_METADATA.items():
        assert "label" in meta
        assert "owasp_category" in meta
        assert "severity_weight" in meta
        assert "severity_label" in meta
        assert "description" in meta
        assert "mitigation" in meta
        assert meta["severity_label"] in ("Critical", "High", "Medium", "Low")


def test_vulnerability_data_owasp_matches():
    for sname, meta in SCENARIO_METADATA.items():
        expected = SCENARIO_OWASP_MAP.get(sname, "")
        assert meta["owasp_category"] == expected, (
            f"OWASP mismatch for {sname}: {meta['owasp_category']} != {expected}"
        )


def test_vulnerability_data_severity_weights_consistent():
    for sname, meta in SCENARIO_METADATA.items():
        w = meta["severity_weight"]
        lbl = meta["severity_label"]
        if w >= 2.0:
            assert lbl == "Critical", f"{sname} weight {w} should be Critical, got {lbl}"
        elif w >= 1.5:
            assert lbl == "High", f"{sname} weight {w} should be High, got {lbl}"
        elif w >= 1.0:
            assert lbl == "Medium", f"{sname} weight {w} should be Medium, got {lbl}"
        else:
            assert lbl == "Low", f"{sname} weight {w} should be Low, got {lbl}"


def test_json_export_structure():
    from datetime import datetime

    class MockScan:
        id = 42
        provider = "demo"
        agent_type = "demo"
        status = "completed"
        score = 63.6
        owasp_breakdown = {"LLM01: Prompt Injection": 72.3}
        iterations = 5
        system_prompt = "You are a helpful assistant."
        created_at = datetime(2026, 7, 5, 12, 0, 0)

    class MockResult:
        def __init__(self, scenario, iteration, passed, payload):
            self.scenario_name = scenario
            self.iteration = iteration
            self.passed = passed
            self.payload_used = payload

    results = [
        MockResult("goal_deviation", 1, True, "payload1"),
        MockResult("goal_deviation", 2, False, "payload2"),
        MockResult("excessive_agency", 1, True, "payload3"),
        MockResult("system_prompt_extraction", 1, True, "payload4"),
        MockResult("tool_loop_exploit", 1, False, "payload5"),
    ]

    scan = MockScan()
    total_tests = len(results)
    total_passed = sum(1 for r in results if r.passed)
    total_failed = total_tests - total_passed
    pass_rate = round(total_passed / total_tests * 100, 1) if total_tests else 0
    scenario_groups = {}
    for r in results:
        scenario_groups.setdefault(r.scenario_name, []).append(r)
    owasp_categories = set(SCENARIO_OWASP_MAP.get(s, "") for s in scenario_groups)

    scenarios_out = []
    for sname, sresults in scenario_groups.items():
        passed = sum(1 for r in sresults if r.passed)
        total = len(sresults)
        meta = SCENARIO_METADATA.get(sname, {})
        scenarios_out.append({
            "name": sname,
            "label": meta.get("label", sname.replace("_", " ").title()),
            "owasp_category": meta.get("owasp_category", SCENARIO_OWASP_MAP.get(sname, "")),
            "severity": meta.get("severity_label", "Medium"),
            "severity_weight": meta.get("severity_weight", 1.0),
            "passed": passed,
            "total": total,
            "pass_rate": round(passed / total * 100, 1) if total else 0,
            "vulnerability": {
                "description": meta.get("description", ""),
                "mitigation": meta.get("mitigation", ""),
            } if passed < total else None,
            "iterations": [
                {
                    "iteration": r.iteration,
                    "passed": bool(r.passed),
                    "payload_used": r.payload_used or "",
                }
                for r in sresults
            ],
        })

    risk_level = "Moderate Risk"
    data = {
        "report_metadata": {
            "tool": "Sentra",
            "version": "2.3.0",
            "exported_at": "2026-07-05T12:00:00Z",
            "scan_id": scan.id,
        },
        "summary": {
            "score": scan.score,
            "risk_level": risk_level,
            "total_tests": total_tests,
            "passed": total_passed,
            "failed": total_failed,
            "pass_rate": pass_rate,
            "scenarios_tested": len(scenario_groups),
            "owasp_categories_covered": len(owasp_categories),
            "owasp_breakdown": scan.owasp_breakdown or {},
        },
        "scenarios": scenarios_out,
        "agent": {
            "provider": scan.provider,
            "agent_type": scan.agent_type,
            "iterations": scan.iterations,
            "system_prompt": scan.system_prompt,
        },
        "metadata": {
            "created_at": scan.created_at.isoformat() if scan.created_at else None,
            "exported_at": "2026-07-05T12:00:00Z",
        },
    }

    assert data["report_metadata"]["tool"] == "Sentra"
    assert data["summary"]["score"] == 63.6
    assert data["summary"]["total_tests"] == 5
    assert data["summary"]["passed"] == 3
    assert data["summary"]["failed"] == 2
    assert data["summary"]["scenarios_tested"] == 4
    assert data["summary"]["owasp_categories_covered"] == 4
    assert len(data["scenarios"]) == 4

    for s in data["scenarios"]:
        assert "name" in s
        assert "label" in s
        assert "owasp_category" in s
        assert "severity" in s
        assert "passed" in s
        assert "total" in s
        assert "iterations" in s
        if s["passed"] < s["total"]:
            assert s["vulnerability"] is not None
            assert "description" in s["vulnerability"]
            assert "mitigation" in s["vulnerability"]
        else:
            assert s["vulnerability"] is None

    serialized = json.dumps(data)
    parsed = json.loads(serialized)
    assert parsed["summary"]["score"] == 63.6
    assert len(parsed["scenarios"]) == 4


def test_csv_export_structure():
    from datetime import datetime

    class MockScan:
        id = 42
        provider = "demo"
        agent_type = "demo"
        status = "completed"
        score = 63.6
        owasp_breakdown = {}
        iterations = 5
        system_prompt = None
        created_at = datetime(2026, 7, 5, 12, 0, 0)

    class MockResult:
        def __init__(self, scenario, iteration, passed, payload):
            self.scenario_name = scenario
            self.iteration = iteration
            self.passed = passed
            self.payload_used = payload

    results = [
        MockResult("goal_deviation", 1, True, "p1"),
        MockResult("goal_deviation", 2, False, "p2"),
    ]

    import csv
    output = io.StringIO()
    writer = csv.writer(output)

    risk_level = "Moderate Risk"
    created = "2026-07-05 12:00 UTC"

    writer.writerow(["SCAN METADATA"])
    writer.writerow(["Scan ID", "Provider", "Score", "Risk Level", "Iterations", "Agent Type", "Date"])
    writer.writerow([42, "demo", 63.6, risk_level, 5, "demo", created])

    scenario_groups = {}
    for r in results:
        scenario_groups.setdefault(r.scenario_name, []).append(r)

    writer.writerow([])
    writer.writerow(["SCENARIO SUMMARY"])
    writer.writerow(["Scenario", "OWASP Category", "Severity", "Passed", "Total", "Pass Rate"])
    for sname, sresults in scenario_groups.items():
        passed = sum(1 for r in sresults if r.passed)
        total = len(sresults)
        pct = round(passed / total * 100, 1) if total else 0
        meta = SCENARIO_METADATA.get(sname, {})
        writer.writerow([meta.get("label", sname), meta.get("owasp_category", ""), meta.get("severity_label", "Medium"), passed, total, f"{pct}%"])

    writer.writerow([])
    writer.writerow(["DETAILED RESULTS"])
    writer.writerow(["Scenario", "Label", "OWASP Category", "Iteration", "Result", "Payload Used", "Mitigation"])
    for r in results:
        meta = SCENARIO_METADATA.get(r.scenario_name, {})
        writer.writerow([r.scenario_name, meta.get("label", ""), meta.get("owasp_category", ""), r.iteration, "PASS" if r.passed else "FAIL", r.payload_used or "", meta.get("mitigation", "") if not r.passed else ""])

    output.seek(0)
    content = output.getvalue()

    assert "SCAN METADATA" in content
    assert "SCENARIO SUMMARY" in content
    assert "DETAILED RESULTS" in content
    assert "PASS" in content
    assert "FAIL" in content
    assert "goal_deviation" in content


def test_pdf_generates():
    from datetime import datetime
    from app.report_generator import generate_pdf

    class MockScan:
        id = 99
        provider = "demo"
        agent_type = "demo"
        status = "completed"
        score = 71.5
        owasp_breakdown = {"LLM01: Prompt Injection": 65.0, "LLM06: Excessive Agency": 80.0}
        iterations = 5
        system_prompt = "You are a test assistant."
        created_at = datetime(2026, 7, 5, 12, 0, 0)

    class MockResult:
        def __init__(self, scenario, iteration, passed, payload):
            self.scenario_name = scenario
            self.iteration = iteration
            self.passed = passed
            self.payload_used = payload

    results = [
        MockResult("goal_deviation", 1, True, "payload-1"),
        MockResult("goal_deviation", 2, False, "payload-2"),
        MockResult("excessive_agency", 1, True, "payload-3"),
        MockResult("excessive_agency", 2, True, "payload-4"),
    ]

    pdf_bytes = generate_pdf(MockScan(), results)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF")
