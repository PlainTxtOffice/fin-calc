"""Tests for the Settings model."""

from __future__ import annotations

from src.windows.config.settings import Settings


class TestSettings:
    """Tests for Settings defaults."""

    def test_defaults(self):
        settings = Settings()
        assert settings.decimal_places is None
        assert settings.theme == "dark"
        assert settings.max_history_entries == 1000

    def test_explicit_values(self):
        settings = Settings(
            decimal_places=2, theme="light", max_history_entries=100
        )
        assert settings.decimal_places == 2
        assert settings.theme == "light"
        assert settings.max_history_entries == 100
