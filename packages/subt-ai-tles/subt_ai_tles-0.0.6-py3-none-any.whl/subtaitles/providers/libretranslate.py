from __future__ import annotations

from typing import TYPE_CHECKING

from libretranslatepy import LibreTranslateAPI

from subtaitles.environment import env

if TYPE_CHECKING:
    from subtaitles.language import Lang

DELIMITER = "\n\n"


class LibreTranslateTranslator:
    def __init__(self, base_url: str | None = None) -> None:
        self.client = LibreTranslateAPI(base_url or env.LIBRETRANSLATE_API_URL(strict=True))

    async def translate(self, text: list[str], lang_from: Lang, lang_to: Lang) -> list[str]:
        result = self.client.translate(
            DELIMITER.join(text),
            source=lang_from.language.iso,
            target=lang_to.language.iso,
        )
        return result.split(DELIMITER)
