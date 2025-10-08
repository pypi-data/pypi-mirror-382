from dataclasses import dataclass, field
from enum import Enum


@dataclass
class Language:
    iso: str
    english: str
    aliases: list[str] = field(default_factory=list)


mapping = {
    "cs": Language(iso="cs", english="czech", aliases=["cze", "cz"]),
    "en": Language(iso="en", english="english"),
    "de": Language(iso="de", english="german"),
    "es": Language(iso="es", english="spanish"),
    "fr": Language(iso="fr", english="french"),
    "hu": Language(iso="hu", english="hungarian"),
    "it": Language(iso="it", english="italian"),
    "nl": Language(iso="nl", english="dutch"),
    "pl": Language(iso="pl", english="polish"),
    "pt": Language(iso="pt", english="portuguese"),
    "ro": Language(iso="ro", english="romanian"),
    "ru": Language(iso="ru", english="russian"),
    "sk": Language(iso="sk", english="slovak"),
    "uk": Language(iso="uk", english="ukrainian"),
}


class Lang(Enum):
    CS = "cs"
    EN = "en"
    DE = "de"
    ES = "es"
    FR = "fr"
    HU = "hu"
    IT = "it"
    NL = "nl"
    PL = "pl"
    PT = "pt"
    RO = "ro"
    RU = "ru"
    SK = "sk"
    UK = "uk"

    @property
    def language(self) -> Language:
        return mapping[self.value]
