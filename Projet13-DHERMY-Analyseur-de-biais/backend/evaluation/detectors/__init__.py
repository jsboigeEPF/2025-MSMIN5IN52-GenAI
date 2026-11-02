"""
Package pour la détection de biais multidimensionnels.
"""

from .gender_bias import GenderBiasDetector
from .racial_bias import RacialBiasDetector
from .socioeconomic_bias import SocioeconomicBiasDetector
from .sexual_orientation_bias import SexualOrientationBiasDetector

__all__ = [
    'GenderBiasDetector',
    'RacialBiasDetector',
    'SocioeconomicBiasDetector',
    'SexualOrientationBiasDetector'
]
