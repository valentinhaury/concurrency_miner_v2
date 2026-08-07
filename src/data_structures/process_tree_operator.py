from enum import Enum

class Operator(Enum):
    Exclusive = "\u00D7"
    Sequence = "\u2192"
    Loop = "\u27f3"
    Arbitrary = "\u2194"
    Interleaving = "\u29E2"
    Concurrent = "\u2227"
    Parallel ="||"
    Multi = "*"
#op.value für das Symbol