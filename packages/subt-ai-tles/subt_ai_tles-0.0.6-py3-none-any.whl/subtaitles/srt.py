import re

srt_markup_patterns = [
    re.compile(r"<.*?>"),
]


def strip_srt_markup(text: list[str]) -> list[str]:
    def __strip(token: str) -> str:
        stripped = token
        for pattern in srt_markup_patterns:
            stripped = re.sub(pattern, "", stripped)

        return stripped

    return [__strip(token) for token in text]
