from .Not import Not
from .Projection import Projection
from .Rename import Rename
from .Selection import Selection

# inverse binding strength
LOGIC_NOT = Not
LOGIC_UNARY_OPERATORS = [
    LOGIC_NOT
]

RA_UNARY_OPERATORS = [
    Projection,
    Rename,
    Selection
]
