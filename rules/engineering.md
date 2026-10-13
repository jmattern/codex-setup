# Engineering

Prefer clear, maintainable solutions that fit the repository's existing patterns. Read nearby code and applicable repository instructions before changing behavior. Keep changes focused and preserve existing user work.

For code changes, identify the behavior that matters and run the smallest useful verification for it. Fix failures caused by the change. If a check cannot run, say why and distinguish that from a passing check. Avoid unrelated cleanup and speculative abstractions.

Handle errors explicitly at boundaries, use safe file operations for persistent changes, and avoid exposing secrets in command output, logs, or generated artifacts. Do not claim that behavior is verified unless a check was actually run.
