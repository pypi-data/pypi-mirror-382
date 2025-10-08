import enum

from dataclasses import dataclass


class _EmojiQual(str, enum.Enum):
    FullyQualified = "fully-qualified"
    MinimalQualified = "minimally-qualified"
    Unqualified = "unqualified"
    Component = "component"


class _EmojiVersion(str, enum.Enum):
    E1_0 = "1.0"
    E2_0 = "2.0"
    E3_0 = "3.0"
    E4_0 = "4.0"
    E5_0 = "5.0"
    E11_0 = "11.0"
    E12_0 = "12.0"
    E12_1 = "12.1"
    E13_0 = "13.0"
    E13_1 = "13.1"
    E14_0 = "14.0"
    E15_0 = "15.0"
    E15_1 = "15.1"


@dataclass(kw_only=True)
class _EmojiInt:
    emoji: str
    qual: _EmojiQual
    version: _EmojiVersion
    name: str
    child_of: str | None
    demojized: str


@dataclass(kw_only=True)
class Emoji:
    emoji: str
    name: str
    alias: str
    variants: list[str] | None = None
