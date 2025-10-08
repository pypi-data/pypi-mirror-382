from typing import Protocol

from subtaitles.language import Lang


class TranslateProtocol(Protocol):
    async def translate(
        self,
        text: list[str],
        language_from: Lang,
        language_to: Lang,
    ) -> list[str]: ...
