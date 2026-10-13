from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
from instruction_utils import build_content  # noqa: E402


def run_script(script: str, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *arguments],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class InstructionToolsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.home = Path(self.temp.name) / "codex-home"
        self.target = self.home / "AGENTS.md"
        self.home_arg = ("--codex-home", str(self.home))

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_build_is_deterministic_and_matches_sources(self) -> None:
        first = run_script("build-instructions")
        self.assertEqual(first.returncode, 0, first.stderr)
        generated = (ROOT / "build" / "AGENTS.md").read_bytes()
        second = run_script("build-instructions")
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(generated, (ROOT / "build" / "AGENTS.md").read_bytes())
        self.assertEqual(generated, build_content())

    def test_preview_does_not_write_and_identical_install_is_noop(self) -> None:
        preview = run_script("install", *self.home_arg)
        self.assertEqual(preview.returncode, 0, preview.stderr)
        self.assertFalse(self.target.exists())

        applied = run_script("install", *self.home_arg, "--apply")
        self.assertEqual(applied.returncode, 0, applied.stderr)
        self.assertEqual(self.target.read_bytes(), build_content())
        backups_before = sorted((self.home / "instruction-backups").iterdir())
        repeated = run_script("install", *self.home_arg, "--apply")
        self.assertEqual(repeated.returncode, 0, repeated.stderr)
        self.assertIn("No change", repeated.stdout)
        self.assertEqual(backups_before, sorted((self.home / "instruction-backups").iterdir()))

    def test_existing_file_requires_explicit_replace_and_is_backed_up(self) -> None:
        self.home.mkdir(parents=True)
        original = b"# My existing instructions\nKeep this.\n"
        self.target.write_bytes(original)
        preview = run_script("install", *self.home_arg)
        self.assertEqual(preview.returncode, 0)
        self.assertIn("different content", preview.stderr)
        self.assertEqual(self.target.read_bytes(), original)

        refused = run_script("install", *self.home_arg, "--apply")
        self.assertEqual(refused.returncode, 2)
        self.assertEqual(self.target.read_bytes(), original)

        applied = run_script("install", *self.home_arg, "--apply", "--replace")
        self.assertEqual(applied.returncode, 0, applied.stderr)
        backups = list((self.home / "instruction-backups").glob("*.bak"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), original)
        rollback = run_script("install", *self.home_arg, "--rollback", "--apply")
        self.assertEqual(rollback.returncode, 0, rollback.stderr)
        self.assertEqual(self.target.read_bytes(), original)

    def test_rollback_of_first_install_restores_absence(self) -> None:
        applied = run_script("install", *self.home_arg, "--apply")
        self.assertEqual(applied.returncode, 0, applied.stderr)
        preview = run_script("install", *self.home_arg, "--rollback")
        self.assertEqual(preview.returncode, 0, preview.stderr)
        self.assertTrue(self.target.exists())
        rollback = run_script("install", *self.home_arg, "--rollback", "--apply")
        self.assertEqual(rollback.returncode, 0, rollback.stderr)
        self.assertFalse(self.target.exists())
        repeated = run_script("install", *self.home_arg, "--rollback", "--apply")
        self.assertEqual(repeated.returncode, 1)
        self.assertIn("already been rolled back", repeated.stderr)

    def test_rollback_refuses_to_overwrite_post_install_edit(self) -> None:
        applied = run_script("install", *self.home_arg, "--apply")
        self.assertEqual(applied.returncode, 0, applied.stderr)
        edited = b"# Later user edit\n"
        self.target.write_bytes(edited)
        rollback = run_script("install", *self.home_arg, "--rollback", "--apply")
        self.assertEqual(rollback.returncode, 1)
        self.assertIn("has changed", rollback.stderr)
        self.assertEqual(self.target.read_bytes(), edited)

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_install_refuses_symlink_target(self) -> None:
        self.home.mkdir(parents=True)
        external = Path(self.temp.name) / "external.md"
        external.write_text("# External\n", encoding="utf-8")
        self.target.symlink_to(external)
        result = run_script("install", *self.home_arg, "--apply", "--replace")
        self.assertEqual(result.returncode, 1)
        self.assertTrue(self.target.is_symlink())
        self.assertEqual(external.read_text(encoding="utf-8"), "# External\n")


if __name__ == "__main__":
    unittest.main()
