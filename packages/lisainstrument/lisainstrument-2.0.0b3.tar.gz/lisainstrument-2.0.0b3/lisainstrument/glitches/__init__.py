"""The glitches package contains tools for obtaining glitch data

This involves an abstract interface representing glitches as continuous functions
of time, in module glitch_source. The glitch_source_interp module provides an
implementation based on spline interpolation. The glitch_file module provides
an abstract interface for reading glitch file data as well as an implementation.
Together, those classes can be used to represent glitch files as continuous
functions.
"""

from .glitch_file import GlitchFile, glitch_file
from .glitch_source import GlitchSource, GlitchSourceZero
from .glitch_source_interp import GlitchSourceSplines
