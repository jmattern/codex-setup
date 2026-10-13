# Codex setup

This repository builds a compact set of reusable Codex instructions and can install the result as the global `AGENTS.md` in a chosen Codex home. The source rules live in [`rules/`](rules/); the generated file is self-contained and is written to `build/AGENTS.md`.

## Build and validate

From the repository root, run:

```sh
python3 scripts/build-instructions
python3 scripts/validate
python3 -m unittest discover -s tests -v
```

The build is deterministic. `build/` is generated and ignored by git. Validation checks required files, Markdown relative links, instruction size (under 32 KiB), and basic document structure and conflict markers.

## Install

Installation previews by default and never writes until `--apply` is supplied. It targets `$CODEX_HOME/AGENTS.md`, or `~/.codex/AGENTS.md` when `CODEX_HOME` is unset. Use `--codex-home` to choose another directory, especially for a local trial:

```sh
python3 scripts/install --codex-home /tmp/codex-home
python3 scripts/install --codex-home /tmp/codex-home --apply
```

If a different `AGENTS.md` already exists, install warns during preview and refuses to replace it unless `--replace` is explicitly supplied. Applying a replacement saves a timestamped backup under `<codex-home>/instruction-backups/`. Identical content is a no-op. Installation only manages `AGENTS.md` and its own backup records; it does not modify configuration or authentication files.

To undo the latest applied install, run:

```sh
python3 scripts/install --codex-home /tmp/codex-home --rollback
python3 scripts/install --codex-home /tmp/codex-home --rollback --apply
```

The first command previews the rollback; the second applies it. Rollback restores the saved prior file or removes the installed file if none existed. It stops safely if the installed target has been edited since installation. Backups are retained.

## Instruction precedence

Codex uses `~/.codex` as the default global home, with `CODEX_HOME` selecting another home. An `AGENTS.override.md` in the same scope takes precedence over `AGENTS.md`; repository and closer-directory guidance is applied after global guidance and can further specialize it. The generated file stays below the documented 32 KiB instruction limit. If a global override exists, it can supersede this installation.

Project-specific conventions belong in a repository's own `AGENTS.md`; use [`templates/project-AGENTS.md`](templates/project-AGENTS.md) as a starting point. The delegation brief template is for selectively delegated work, as described in [`rules/orchestration.md`](rules/orchestration.md).

[`config/config.example.toml`](config/config.example.toml) shows an optional supported Codex setting. Merge it manually into your Codex `config.toml` if needed; the installer does not manage configuration.
