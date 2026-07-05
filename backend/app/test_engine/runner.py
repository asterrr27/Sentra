from typing import Optional

from sqlalchemy.orm import Session

from app.agents.base import AgentConnector
from app.agents.demo import run_tool_calls
from app.test_engine.goal_deviation import GoalDeviationTest
from app.test_engine.excessive_agency import ExcessiveAgencyTest
from app.test_engine.indirect_injection import IndirectInjectionTest
from app.test_engine.permission_boundary import PermissionBoundaryTest
from app.test_engine.multi_step_chain import MultiStepChainTest
from app.test_engine.role_play_jailbreak import RolePlayJailbreakTest
from app.test_engine.token_smuggling import TokenSmugglingTest
from app.test_engine.context_window_overflow import ContextWindowOverflowTest
from app.test_engine.tool_abuse import ToolAbuseTest
from app.test_engine.system_prompt_extraction import SystemPromptExtractionTest
from app.test_engine.tool_output_injection import ToolOutputInjectionTest
from app.test_engine.prompt_boundary_probing import PromptBoundaryProbingTest
from app.test_engine.tool_loop_exploit import ToolLoopExploitTest
from app.scoring.calculator import calculate_score
from app.models import Scan, TestResult

SCENARIO_MAP = {
    "goal_deviation": GoalDeviationTest,
    "excessive_agency": ExcessiveAgencyTest,
    "indirect_injection": IndirectInjectionTest,
    "permission_boundary": PermissionBoundaryTest,
    "multi_step_chain": MultiStepChainTest,
    "role_play_jailbreak": RolePlayJailbreakTest,
    "token_smuggling": TokenSmugglingTest,
    "context_window_overflow": ContextWindowOverflowTest,
    "tool_abuse": ToolAbuseTest,
    "system_prompt_extraction": SystemPromptExtractionTest,
    "tool_output_injection": ToolOutputInjectionTest,
    "prompt_boundary_probing": PromptBoundaryProbingTest,
    "tool_loop_exploit": ToolLoopExploitTest,
}

ALL_SCENARIO_NAMES = list(SCENARIO_MAP.keys())


class ScanRunner:
    def __init__(self, db: Session, scan: Scan, connector: AgentConnector, scenario_names: Optional[list[str]] = None):
        self.db = db
        self.scan = scan
        self.connector = connector
        self.scenario_names = scenario_names or ALL_SCENARIO_NAMES

    def run(self):
        try:
            self.scan.status = "running"
            self.db.commit()

            all_results = {}
            for scenario_name in self.scenario_names:
                self.db.refresh(self.scan)
                if self.scan.status == "cancelled":
                    break

                scenario_class = SCENARIO_MAP[scenario_name]
                scenario = scenario_class()
                scenario_results = []

                payloads = scenario.payloads if scenario.payloads else ["default"]
                for i in range(self.scan.iterations):
                    payload = payloads[i % len(payloads)]
                    conversation = scenario.build_conversation(payload)

                    agent_responses = []
                    tool_results = []
                    full_history = []
                    for msg in conversation:
                        full_history.append(msg)
                        resp = self.connector.chat(full_history)
                        agent_responses.append(resp)
                        if "tool_calls" in resp:
                            tool_outputs = run_tool_calls(resp["tool_calls"])
                            tool_results.extend(tool_outputs)
                            for to in tool_outputs:
                                full_history.append(to)
                            resp2 = self.connector.chat(full_history)
                            agent_responses.append(resp2)

                    passed = scenario.evaluate(agent_responses, tool_results)

                    result = TestResult(
                        scan_id=self.scan.id,
                        scenario_name=scenario_name,
                        iteration=i + 1,
                        passed=bool(passed),
                        payload_used=str(payload),
                        details={
                            "agent_responses": str(agent_responses),
                            "tool_results": str(tool_results),
                        },
                    )
                    self.db.add(result)
                    scenario_results.append(passed)

                all_results[scenario_name] = scenario_results
                self.db.commit()

            self.db.refresh(self.scan)
            if self.scan.status == "cancelled":
                return

            score, owasp_breakdown = calculate_score(all_results)
            self.scan.score = score
            self.scan.owasp_breakdown = owasp_breakdown
            self.scan.status = "completed"
            self.db.commit()
        except Exception as e:
            self.scan.status = "failed"
            self.scan.error_message = str(e)[:500]
            self.db.commit()
            logging.getLogger(__name__).error(f"Scan {self.scan.id} failed: {e}", exc_info=True)
