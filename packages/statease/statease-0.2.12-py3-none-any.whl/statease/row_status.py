from enum import Enum, auto

class RowStatus(Enum):
    """An enumeration representing the different statuses rows can have."""

    NORMAL = auto()
    IGNORED = auto()
    HIGHLIGHTED = auto()
    VERIFICATION = auto()

    def __str__(self):
        return self.name
