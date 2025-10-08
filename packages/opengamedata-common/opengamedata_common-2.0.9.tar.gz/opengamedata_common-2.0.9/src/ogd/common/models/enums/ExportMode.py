# import standard libraries
from enum import IntEnum

class ExportMode(IntEnum):
    EVENTS     = 1
    DETECTORS  = 2
    FEATURES   = 3
    SESSION    = 4
    PLAYER     = 5
    POPULATION = 6

    def __str__(self):
        return self.name
