"""Provider adapters. Each turns (system, messages) into text with token usage; nothing else is provider-specific."""

from .base import Completion, Provider


def get_provider(reviewer: dict) -> Provider:
    kind = reviewer["provider"]
    if kind == "anthropic":
        from .anthropic import AnthropicProvider
        return AnthropicProvider(reviewer)
    if kind == "claude-code":
        from .claude_code import ClaudeCodeProvider
        return ClaudeCodeProvider(reviewer)
    raise NotImplementedError(f"no adapter yet for provider {kind!r} (milestone M6)")


__all__ = ["Completion", "Provider", "get_provider"]
