"""
Coin Counter - A computer vision-based coin detection and counting system.

This package provides both CLI and GUI interfaces for detecting and counting
coins in images using computer vision techniques (ORB feature matching with
Hough Circle Transform or Contour detection).
"""

__version__ = "2.0.1"
__author__ = "Ibteeker Mahir Ishum"
__email__ = "mhrisham@gmail.com"

from .coin_counter_cli import (
    save_reference,
    load_references,
    detect_and_identify,
    detect_circles_hough,
    detect_circles_contour,
    load_metadata,
    save_metadata,
    make_orb,
    compute_orb_features,
    match_features,
    extract_circle,
    identify_coin,
)

__all__ = [

    "__version__",
    "__author__",
    "__email__",

    "save_reference",
    "load_references",
    "detect_and_identify",
    "detect_circles_hough",
    "detect_circles_contour",
    "load_metadata",
    "save_metadata",

    "make_orb",
    "compute_orb_features",
    "match_features",
    "extract_circle",
    "identify_coin",
]
