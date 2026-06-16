"""Type definitions for DOPEHOUSE OPENMIC."""

from typing import Literal

SunoModel = Literal[
    "chirp-v3-0",
    "chirp-v3-5",
    "chirp-v4",
    "chirp-v4-5",
    "chirp-v4-5-plus",
    "chirp-v5",
    "chirp-v5-5",
]

LyricsModel = Literal["default", "remi-v1"]

VocalGender = Literal["", "f", "m"]

VariationCategory = Literal["high", "normal", "subtle"]

DEFAULT_MODEL: SunoModel = "chirp-v5-5"

DEFAULT_LYRICS_MODEL: LyricsModel = "default"
