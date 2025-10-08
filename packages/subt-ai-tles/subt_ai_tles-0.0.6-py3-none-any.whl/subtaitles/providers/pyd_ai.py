from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic_ai import Agent

from subtaitles.environment import env

if TYPE_CHECKING:
    from subtaitles import Lang


class PydanticAiTranslator:
    @staticmethod
    async def translate(
        text: list[str],
        language_from: Lang,
        language_to: Lang,
        model: str | None = None,
    ) -> list[str]:
        agent = Agent(
            model=model or env.OPENAI_MODEL(strict=True),
            instructions=f"Translate subtitles from {language_from.value.english} to "
            f"{language_to.value.english} accurately while "
            "maintaining the original meaning and tone. Use natural-sounding "
            "phrases and idioms that accurately convey the meaning "
            "of the original text.",
            output_type=list[str],
        )
        return (await agent.run(text)).output
