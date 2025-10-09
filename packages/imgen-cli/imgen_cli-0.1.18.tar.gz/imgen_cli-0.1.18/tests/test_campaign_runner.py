from __future__ import annotations

import pytest

from imagemcp.campaign.runner import (
    DeterministicProviderError,
    enforce_deterministic_provider,
)


def test_enforce_deterministic_provider_accepts_aliases() -> None:
    enforce_deterministic_provider("openrouter")
    enforce_deterministic_provider("openrouter:gemini-2.5-flash-image-preview")
    enforce_deterministic_provider("mock")


def test_enforce_deterministic_provider_rejects_unknown() -> None:
    with pytest.raises(DeterministicProviderError) as exc:
        enforce_deterministic_provider("anthropic:claude")
    assert "Allowed providers" in str(exc.value)
