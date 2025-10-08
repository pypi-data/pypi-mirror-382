"""Backwards-compatibility alias for historical imports.

This file provides a harmless alias to the new implementation. Prefer
importing `MoonRuneShards` directly from `act3.items` in new code.
"""
from .MoonRuneShards import MoonRuneShards as CoquinaRunes

__all__ = ["CoquinaRunes"]
