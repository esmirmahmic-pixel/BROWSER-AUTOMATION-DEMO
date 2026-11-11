"""Unit tests for report state transitions, without a nested pytest session."""
from types import SimpleNamespace
from tests import conftest as hooks

def report(node,when,outcome,duration=.01):
    return SimpleNamespace(nodeid=node,when=when,duration=duration,
        failed=outcome=='failed',passed=outcome=='passed',skipped=outcome=='skipped',longrepr='failure')

def test_setup_failure_recorded_once(monkeypatch):
    local = {}
    with monkeypatch.context() as m:
        m.setattr(hooks, "_OUTCOMES", local)
        hooks.pytest_runtest_logreport(report('test_a','setup','failed'))
        hooks.pytest_runtest_logreport(report('test_a','teardown','passed'))
        assert len(hooks._OUTCOMES)==1 and hooks._OUTCOMES['test_a']['failed']

def test_teardown_failure_overrides_call_pass(monkeypatch):
    local = {}
    with monkeypatch.context() as m:
        m.setattr(hooks, "_OUTCOMES", local)
        hooks.pytest_runtest_logreport(report('test_a','call','passed'))
        hooks.pytest_runtest_logreport(report('test_a','teardown','failed'))
        assert hooks._OUTCOMES['test_a']['failed'] and hooks._OUTCOMES['test_a']['passed']

def test_skipped_setup_remains_skipped(monkeypatch):
    local = {}
    with monkeypatch.context() as m:
        m.setattr(hooks, "_OUTCOMES", local)
        hooks.pytest_runtest_logreport(report('test_a','setup','skipped'))
        assert not hooks._OUTCOMES['test_a']['failed'] and not hooks._OUTCOMES['test_a']['passed']
