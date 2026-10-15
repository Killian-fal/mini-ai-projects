# loaded by `make test` (`pytest -p interactive_support_flow_test.coverage.plugin`): the run fails while a transition
# of a flow tested with FlowTest is taken by no FlowTest
import pytest

from interactive_support_flow_test.coverage.transitions import missing


def pytest_sessionfinish(session: pytest.Session):
    if missing() and session.exitstatus == pytest.ExitCode.OK:
        session.exitstatus = pytest.ExitCode.TESTS_FAILED


def pytest_terminal_summary(terminalreporter: pytest.TerminalReporter):
    if transitions := missing():
        terminalreporter.section("flow coverage: transitions never taken", red=True)
        for transition in transitions:
            terminalreporter.write_line(transition)
