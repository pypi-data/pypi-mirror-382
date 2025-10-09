from enum import StrEnum
from maleo.types.string import ListOfStrings


class Usage(StrEnum):
    REGULAR = "regular"
    AGGREGATE = "aggregate"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]


class Status(StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"
    OVERLOAD = "overload"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]
