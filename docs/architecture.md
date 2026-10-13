# Architecture

The five files in [`../rules/`](../rules/) are the maintained instruction sources. `scripts/build-instructions` joins them in a fixed order with a short preamble and writes a deterministic, self-contained `build/AGENTS.md`. The generated file is ignored by git and can be rebuilt at any time.

`scripts/install` builds the same content in memory and targets only `<codex-home>/AGENTS.md`. Preview is the default. Applying a replacement saves the prior bytes under `instruction-backups/`, then writes the new file atomically and records the expected installed hash. Rollback compares the current target with that hash before restoring the saved bytes, or removing the file when the first install created it. A mismatch stops rollback to protect later edits. Symbolic link targets are refused.

The installer does not read or write Codex configuration or authentication data. `--codex-home` and the environment variable `CODEX_HOME` select a home; absent either, the default is `~/.codex`. A different existing `AGENTS.md` requires `--replace` for an applied install. Identical content returns without creating another backup or transaction.

`scripts/validate` checks the repository's expected files, relative Markdown links, conflict-marker strings, top-level headings, expected generated sections, and the 32 KiB instruction size bound. These are lightweight structural checks: they do not parse all Markdown syntax or prove semantic consistency.
