"""
Default values for chartviz functions.
"""

from omgui.chartviz.types import OutputType, BarModeType

# Main
OUTPUT: OutputType = "svg"
OPTIONS: dict = None

# Shared options
TITLE: str = None
SUBTITLE: str = None
BODY: str = None
X_TITLE: str = None
Y_TITLE: str = None
X_PREFIX: str = None
Y_PREFIX: str = None
X_SUFFIX: str = None
Y_SUFFIX: str = None
WIDTH: int = 600
HEIGHT: int = 400
SCALE: float = 1.0
OMIT_LEGEND: bool = False
RETURN_DATA: bool = False

# Function-specific options
HORIZONTAL: bool = False
BARMODE: BarModeType = "overlay"  # for histogram
SHOW_POINTS: str = False  # for box plot
BOXMEAN: bool = False  # for box plot
