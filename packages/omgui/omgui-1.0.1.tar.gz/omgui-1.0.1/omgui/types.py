"""
Global type aliases for omgui.

The 'annotations' lib lets us type hint without having to load
entire libraries on startup, but we need to use older Union syntax
to combine strings and other types.
"""

from __future__ import annotations
from typing import TypeAlias, Union


PropDataType: TypeAlias = Union[list[any], list[dict[str, any]], "pd.DataFrame"]
