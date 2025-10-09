"""The freqplan subpackage contains tools for obtaining frequency plan data

This involves an abstract interface FreqPlanSource representing arbitrary sources
of frequency plan data as continuous functions (defined in module fplan_source)
and implementations. The FreqPlanSourceFile implementation is using spline
interpolation. Finally, there is a class FreqPlanFile for reading frequency
plan files. Combining those one can represent frequency file data as continous
functions.
"""

from .fplan_file import FreqPlanFile
from .fplan_source import FreqPlanSource
from .fplan_source_interp import FreqPlanSourceFile
