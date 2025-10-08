from __future__ import annotations

import os


class EnvVar:
    def __init__(self, key: str, default: str | None = None) -> None:
        self.key = key
        self.default = default

    def __call__(self, *, strict: bool = False) -> str | None:
        val = os.getenv(self.key, None)
        if not val:
            val = self.default

        if not val and strict:
            msg = f"Missing environment variable: '{self.key}'"
            raise ValueError(msg)

        return val

    @property
    def value(self) -> str | None:
        return self()


class EnvVars:
    OPENAI_API_KEY = EnvVar("OPENAI_API_KEY")
    OPENAI_ORG_ID = EnvVar("OPENAI_ORG_ID")
    OPENAI_MODEL = EnvVar("OPENAI_MODEL", "gpt-5-nano")
    LIBRETRANSLATE_API_URL = EnvVar("LIBRETRANSLATE_API_URL")
    CACHE_DIR = EnvVar("SRT_CACHE_DIR")


env = EnvVars()
