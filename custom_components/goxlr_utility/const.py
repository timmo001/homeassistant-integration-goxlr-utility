"""Constants for the GoXLR Utility integration."""
from typing import Final

from goxlrutilityapi.exceptions import (
    ConnectionClosedException,
    ConnectionErrorException,
)

DOMAIN: Final[str] = "goxlr_utility"

CONNECTION_ERRORS: Final = (
    ConnectionClosedException,
    ConnectionErrorException,
    ConnectionResetError,
)

NAME_MAP = {
    "bleep": "Bleep",
    "cough": "Cough",
    "effect_fx": "Effect FX",
    "effect_hard_tune": "Effect Hard Tune",
    "effect_megaphone": "Effect Megaphone",
    "effect_robot": "Effect Robot",
    "effect_select1": "Effect Select 1",
    "effect_select2": "Effect Select 2",
    "effect_select3": "Effect Select 3",
    "effect_select4": "Effect Select 4",
    "effect_select5": "Effect Select 5",
    "effect_select6": "Effect Select 6",
    "fader1_mute": "Fader 1 Mute",
    "fader2_mute": "Fader 2 Mute",
    "fader3_mute": "Fader 3 Mute",
    "fader4_mute": "Fader 4 Mute",
    "LineIn": "Line In",
    "mic": "Microphone",
    "Mic": "Microphone",
    "sampler_bottom_left": "Sampler Bottom Left",
    "sampler_bottom_right": "Sampler Bottom Right",
    "sampler_clear": "Sampler Clear",
    "sampler_select_a": "Effect Sampler A",
    "sampler_select_b": "Effect Sampler B",
    "sampler_select_c": "Effect Sampler C",
    "sampler_top_left": "Sampler Top Left",
    "sampler_top_right": "Sampler Top Right",
}
