import unittest
import tempfile
import shutil
import subprocess
import sys
import os
from pathlib import Path
from textwrap import dedent

from ariadne import Theseus
from ariadne.ariadne import get_git_hash, get_jj_changeset


class TestExceptionHandlingEndToEnd(unittest.TestCase):
    """End-to-end tests for exception handling and resume functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test.db"
        self.exp_dir = Path(self.temp_dir) / "experiments"
        self.theseus = Theseus(
            db_path=self.db_path,
            exp_dir=self.exp_dir,
            loglevel=Theseus.LogLevel.NONE
        )

    def tearDown(self):
        """Clean up test fixtures."""
        self.theseus._cleanup(-1)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_test_script(self, script_name: str, script_content: str) -> Path:
        """Create a test script in the temp directory."""
        script_path = Path(self.temp_dir) / script_name
        with open(script_path, 'w') as f:
            f.write(script_content)
        return script_path

    def test_exception_leaves_experiment_incomplete(self):
        """Test that a script raising an exception leaves the experiment incomplete."""

        # Create a script that raises an exception
        ariadne_parent = Path(__file__).parent
        failing_script = self._create_test_script("failing_script.py", dedent(f'''
            import sys
            sys.path.insert(0, "{ariadne_parent}")

            from ariadne import Theseus
            from pathlib import Path

            # Initialize Theseus with the same DB and exp_dir
            theseus = Theseus(
                db_path=Path("{self.db_path}"),
                exp_dir=Path("{self.exp_dir}"),
                loglevel=Theseus.LogLevel.NONE
            )

            # Start an experiment
            exp_id, run_folder = theseus.start({{"param": "value"}}, "failing_exp", "This will fail")

            # Do some work
            print(f"Started experiment {{exp_id}} in {{run_folder}}")

            # Simulate an exception during the experiment
            raise ValueError("Simulated failure during experiment")
        '''))

        # Run the failing script as a subprocess
        result = subprocess.run([sys.executable, str(failing_script)],
                              capture_output=True, text=True)

        # The script should have failed with non-zero exit code
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ValueError: Simulated failure during experiment", result.stderr)

        # Check that the experiment exists but is incomplete
        experiments = self.theseus.get("failing_exp")
        self.assertEqual(len(experiments), 1)

        exp = experiments[0]
        self.assertTrue(exp.name.startswith("failing_exp"))
        self.assertFalse(exp.completed, "Experiment should be incomplete due to exception")
        self.assertIsNone(exp.end_timestamp, "End timestamp should be None for incomplete experiment")

    def test_successful_run_marks_experiment_complete(self):
        """Test that a successful script marks the experiment as complete."""

        # Create a script that completes successfully
        ariadne_parent = Path(__file__).parent
        success_script = self._create_test_script("success_script.py", dedent(f'''
            import sys
            sys.path.insert(0, "{ariadne_parent}")

            from ariadne import Theseus
            from pathlib import Path

            # Initialize Theseus with the same DB and exp_dir
            theseus = Theseus(
                db_path=Path("{self.db_path}"),
                exp_dir=Path("{self.exp_dir}"),
                loglevel=Theseus.LogLevel.NONE
            )

            # Start an experiment
            exp_id, run_folder = theseus.start({{"param": "value"}}, "success_exp", "This will succeed")

            # Do some work
            print(f"Started experiment {{exp_id}} in {{run_folder}}")

            # Exit normally - this should trigger cleanup and mark as complete
            print("Experiment completed successfully")
        '''))

        # Run the successful script as a subprocess
        result = subprocess.run([sys.executable, str(success_script)],
                              capture_output=True, text=True)

        # The script should have succeeded
        self.assertEqual(result.returncode, 0)
        self.assertIn("Experiment completed successfully", result.stdout)

        # Check that the experiment is marked as complete
        experiments = self.theseus.get("success_exp")
        self.assertEqual(len(experiments), 1)

        exp = experiments[0]
        self.assertTrue(exp.completed, "Experiment should be complete for successful run")
        self.assertIsNotNone(exp.end_timestamp, "End timestamp should be set for completed experiment")

    def test_keyboard_interrupt_leaves_experiment_incomplete(self):
        """Test that KeyboardInterrupt (Ctrl+C) leaves experiment incomplete."""

        # Create a script that simulates a KeyboardInterrupt
        ariadne_parent = Path(__file__).parent
        interrupt_script = self._create_test_script("interrupt_script.py", dedent(f'''
            import sys
            sys.path.insert(0, "{ariadne_parent}")

            from ariadne import Theseus
            from pathlib import Path
            import signal
            import os

            theseus = Theseus(
                db_path=Path("{self.db_path}"),
                exp_dir=Path("{self.exp_dir}"),
                loglevel=Theseus.LogLevel.NONE
            )

            exp_id, run_folder = theseus.start({{"param": "value"}}, "interrupt_exp", "Will be interrupted")
            print(f"INTERRUPT_EXP_ID:{{exp_id}}")

            # Simulate a KeyboardInterrupt (SIGINT)
            os.kill(os.getpid(), signal.SIGINT)
        '''))

        # Run the interrupt script
        result = subprocess.run([sys.executable, str(interrupt_script)],
                              capture_output=True, text=True)

        # Should have been interrupted (negative exit code or specific signal code)
        self.assertNotEqual(result.returncode, 0)

        # Extract experiment ID
        interrupt_exp_id = None
        for line in result.stdout.split('\n'):
            if line.startswith("INTERRUPT_EXP_ID:"):
                interrupt_exp_id = int(line.split(':')[1])
                break

        self.assertIsNotNone(interrupt_exp_id, "Interrupt script should have created an experiment")
        assert interrupt_exp_id is not None  # Type checker hint

        # Verify experiment is incomplete due to interruption
        exp = self.theseus.get_by_id(interrupt_exp_id)
        self.assertFalse(exp.completed, "Interrupted experiment should remain incomplete")
        self.assertIsNone(exp.end_timestamp, "Interrupted experiment should have no end timestamp")

if __name__ == "__main__":
    unittest.main(verbosity=2)