"""Exceptions related to language models."""

# pylint: disable=line-too-long, missing-module-docstring, keyword-arg-before-vararg, missing-function-docstring

from __future__ import annotations

from typing import Any, Optional, Sequence, overload

from autorag.types.language_models import ContentPolicyError


class ContentPolicyViolationException(Exception):
    """
    Exception raised when the model reports content-policy violations.

    Behaves like a normal Exception (message + *args) but carries a
    `content_policy_violations` attribute with structured details.
    """

    # Typing-friendly overloads (for linters/type checkers)
    @overload
    def __init__(
        self, content_policy_violations: Sequence[ContentPolicyError]
    ) -> None: ...
    @overload
    def __init__(
        self,
        content_policy_violations: Sequence[ContentPolicyError],
        message: str,
        *args: Any,
    ) -> None: ...
    @overload
    def __init__(
        self,
        content_policy_violations: Sequence[ContentPolicyError],
        message: None = None,
        *args: Any,
    ) -> None: ...

    def __init__(
        self,
        content_policy_violations: Sequence[ContentPolicyError],
        message: Optional[str] = None,
        *args: Any,
    ) -> None:
        # Store violations first (available even if something downstream inspects mid-construct)
        self.content_policy_violations = list(content_policy_violations)

        # Default message if none provided
        if message is None:
            cats = sorted(
                {v.content_policy_type for v in self.content_policy_violations}
            )
            message = (
                f"{len(self.content_policy_violations)} content policy violation(s)"
                + (f": {', '.join(cats)}" if cats else "")
            )

        # Delegate to Exception to keep normal behavior (args, pickling, etc.)
        super().__init__(message, *args)

    # Optional: keep a friendly alias
    @property
    def violations(self) -> list[ContentPolicyError]:
        return self.content_policy_violations

    # Optional: helpful repr for logs
    def __repr__(self) -> str:
        base = super().__repr__()
        return f"{self.__class__.__name__}({base}, violations={len(self.content_policy_violations)})"
