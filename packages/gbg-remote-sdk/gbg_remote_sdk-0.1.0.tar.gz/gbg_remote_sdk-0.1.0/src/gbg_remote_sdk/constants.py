from enum import Enum

INSTRUMENT_STATUS_VARIABLE_NAME_SUFFIX = ".Status"
type InstrumentName = str


class ProgramStatus(str, Enum):
    IDLE = "Idle"
    RUNNING = "Running"
    PAUSED = "Paused"
    ERROR = "Error"


class InstrumentStatus(str, Enum):
    READY = "Ready"
    BUSY = "Busy"
    ERROR = "Error"
    LOCKED = "Locked"
    UNKNOWN = "Unknown"


class OrderStatus(str, Enum):
    UNKNOWN = "Unkown"  # yes, this is really misspelled in the API response # spellchecker:disable-line
    CANCELED = "Canceled"
    COMPLETE = "Complete"
    RUNNING = "Running"
    SCHEDULED = "Scheduled"  # TODO: explicitly test this---but it was observed in the wild
    ERROR = "Error"  # guessing that this is possible in a fixed version of GBG, but not tested yet
