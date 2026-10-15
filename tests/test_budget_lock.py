"""Exercise the actual deployment gate with no provider commands available."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import textwrap
import unittest

from tools.validate_budget_lock import is_fresh_open


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "deploy.yml"
EXPECTED_READ = (
    "secrets versions access latest --secret=cloud-run-budget-lock "
    "--project=neon-glyph-491500-e2"
)


def workflow_gate():
    workflow = WORKFLOW.read_text()
    step = workflow.split("      - name: Enforce Cloud Run budget lock\n", 1)[1]
    block = step.split("      - name:", 1)[0].split("        run: |\n", 1)[1]
    return textwrap.dedent(block)


class BudgetLockWorkflowTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="freshsky-budget-test-")
        self.addCleanup(directory.cleanup)
        self.directory = Path(directory.name)
        self.bin = self.directory / "bin"
        self.bin.mkdir()
        self.log = self.directory / "calls.txt"
        python = self.bin / "python3"
        python.write_text(f"#!/bin/sh\nexec {shlex.quote(sys.executable)} \"$@\"\n")
        python.chmod(0o755)

    def run_gate(self, value="", status=0, *, missing_command=False):
        gcloud = self.bin / "gcloud"
        if not missing_command:
            gcloud.write_text(
                "#!/bin/sh\n"
                'printf "%s\\n" "$*" >> "$MOCK_LOG"\n'
                f'[ "$*" = {shlex.quote(EXPECTED_READ)} ] || exit 99\n'
                'printf "%s" "$MOCK_VALUE"\n'
                'printf "%s" "private provider diagnostic" >&2\n'
                'exit "$MOCK_STATUS"\n'
            )
            gcloud.chmod(0o755)
        self.log.write_text("")
        # PATH contains only our mock and the Python wrapper. No real gcloud,
        # network tool, ambient credentials, or inherited shell config is used.
        result = subprocess.run(
            ["/bin/bash", "-c", workflow_gate()],
            cwd=ROOT,
            env={
                "PATH": str(self.bin),
                "HOME": str(self.directory),
                "PYTHONDONTWRITEBYTECODE": "1",
                "MOCK_LOG": str(self.log),
                "MOCK_VALUE": value,
                "MOCK_STATUS": str(status),
            },
            text=True,
            capture_output=True,
            check=False,
            timeout=10,
        )
        self.assertEqual(
            self.log.read_text().splitlines(),
            [] if missing_command else [EXPECTED_READ],
        )
        self.assertNotIn("private provider diagnostic", result.stdout + result.stderr)
        return result

    def test_fresh_timestamped_open_allows_gate(self):
        now = datetime.now(timezone.utc)
        for opened_at in (now, now - timedelta(hours=29), now + timedelta(minutes=1)):
            with self.subTest(opened_at=opened_at):
                self.assertEqual(self.run_gate(f"open:{opened_at.isoformat()}").returncode, 0)

    def test_missing_denied_network_and_other_read_errors_fail_closed(self):
        fresh = f"open:{datetime.now(timezone.utc).isoformat()}"
        for reason, status in (("missing", 1), ("denied", 7), ("network", 14), ("other", 42)):
            with self.subTest(reason=reason):
                # Even fresh-looking stdout cannot authorize a failed read.
                result = self.run_gate(fresh, status)
                self.assertEqual(result.returncode, 1)
                self.assertIn("missing or unreadable", result.stdout)

    def test_missing_gcloud_fails_closed(self):
        result = self.run_gate(missing_command=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("missing or unreadable", result.stdout)

    def test_empty_locked_throttled_and_malformed_values_fail_closed(self):
        for value in (
            "", "   ", "open", "closed", "locked:v3:50", "throttled:v3:45",
            "open:not-a-date", "open:2026-99-99T99:99:99Z",
            "open:2026-10-15T12:00:00", "OPEN:2026-10-15T12:00:00Z",
            "open:2026-10-15T12:00:00Z\nopen:2026-10-15T12:00:00Z",
        ):
            with self.subTest(value=value):
                result = self.run_gate(value)
                self.assertEqual(result.returncode, 1)
                self.assertIn("not fresh open", result.stdout)

    def test_stale_and_future_timestamped_open_fail_closed(self):
        now = datetime.now(timezone.utc)
        for opened_at in (now - timedelta(hours=31), now + timedelta(minutes=3)):
            with self.subTest(opened_at=opened_at):
                self.assertEqual(self.run_gate(f"open:{opened_at.isoformat()}").returncode, 1)

    def test_gate_precedes_candidate_creation_and_workflow_stays_manual(self):
        workflow = WORKFLOW.read_text()
        self.assertIn("workflow_dispatch:", workflow)
        self.assertNotIn("push:", workflow)
        self.assertNotIn("schedule:", workflow)
        self.assertLess(
            workflow.index("- name: Enforce Cloud Run budget lock"),
            workflow.index("- name: Create and verify zero-traffic candidate"),
        )


class BudgetLockContractTests(unittest.TestCase):
    def test_existing_age_and_future_skew_boundaries(self):
        now = datetime(2026, 10, 15, 20, 0, tzinfo=timezone.utc)
        cases = (
            (now - timedelta(hours=30), True),
            (now - timedelta(hours=30, microseconds=1), False),
            (now + timedelta(minutes=2), True),
            (now + timedelta(minutes=2, microseconds=1), False),
        )
        for opened_at, allowed in cases:
            with self.subTest(opened_at=opened_at):
                self.assertEqual(is_fresh_open(f"open:{opened_at.isoformat()}", now=now), allowed)

    def test_timezone_offsets_and_z_are_equivalent(self):
        now = datetime(2026, 10, 15, 20, 0, tzinfo=timezone.utc)
        for value in ("open:2026-10-15T20:00:00Z", "open:2026-10-15T16:00:00-04:00"):
            with self.subTest(value=value):
                self.assertTrue(is_fresh_open(value, now=now))


if __name__ == "__main__":
    unittest.main()


# Existing tests supply synthetic model responses; account eligibility is explicit.
import pytest as _free_policy_pytest
@_free_policy_pytest.fixture(autouse=True)
def _verified_free_test_context(monkeypatch):
    import app as _test_app
    monkeypatch.setattr(_test_app, '_ai_availability', lambda: {'available': True})
