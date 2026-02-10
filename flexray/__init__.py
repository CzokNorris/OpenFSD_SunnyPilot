"""
FlexRay Support for Panda Experiments

This package provides FlexRay protocol support for experimental Panda devices.
FlexRay is a high-speed, deterministic automotive communication protocol used
in modern luxury vehicles.
"""

from .protocol import (
    FlexRayTiming,
    FlexRayFrame,
    FlexRayBusConfig,
    FlexRayState,
    FlexRayError,
    FlexRayCommand,
    FlexRayFlags,
    calculate_frame_crc,
    format_frame_id,
    FLEXRAY_VERSION
)

__version__ = "0.1.0"
__all__ = [
    'FlexRayTiming',
    'FlexRayFrame',
    'FlexRayBusConfig',
    'FlexRayState',
    'FlexRayError',
    'FlexRayCommand',
    'FlexRayFlags',
    'calculate_frame_crc',
    'format_frame_id',
    'FLEXRAY_VERSION',
]
