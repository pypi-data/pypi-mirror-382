"""
CDCL Protocol Command and Response Prefixes

These enums serve as the source-of-truth for what prefixes to use for specific
commands and what prefix to expect in response.
"""

from typing import Union
from enum import Enum

# ----------------- Instructions ---------------------


class GenericInstructionPrefixes(str, Enum):
    """Generic instruction prefixes for all devices"""
    GET_CHILDREN = 'h'
    GET_FILE = 'F'
    GET_INFO = 'i'
    GET_QC_MODE_KEY = 'k'
    GET_STATUS = 'x'
    GET_TIMESTAMP = 'Z'
    LIST_FILES = 'f'
    READ_XBEE_BUFFER = 'w'
    REBOOT = '0'
    SET_DEMO_MODE = 'd'
    SET_MODEL_NUMBER = 'N'
    SET_SERIAL_NUMBER = 'n'
    SET_TIMESTAMP = 'z'
    TURN_QC_MODE_OFF = 'q'
    TURN_QC_MODE_ON = 'Q'
    UNLOCK_DEMO = 'u'
    GET_SETTINGS = 'G'
    SET_SETTINGS = 'g'
    LIST_EXPERIMENTS = 'e'
    GET_EXPERIMENT = 'E'
    GET_STORAGE_MODIFIED_TIMESTAMP = 'm'


class PlateReaderSpecificInstructionPrefixes(str, Enum):
    """Plate reader specific instruction prefixes"""
    CALIBRATE = 'c'
    BLINK = 'b'
    READ_PLATE = 'R'
    READ_WELL = 'r'
    SET_STATUS_LED = 'L'
    SET_LED = 'l'
    START = 'S'
    STOP = 's'
    GET_TEMPERATURE = 't'
    EXPERIMENT_SETUP = 'A'
    SET_WAVELENGTHS = 'v'
    GET_WAVELENGTHS = 'V'
    GET_IREF = 'J'
    SET_IREF = 'j'


class CanopySpecificInstructionPrefixes(str, Enum):
    """Canopy specific instruction prefixes"""
    STRESS_MODE_ON = 'M'
    STRESS_MODE_OFF = 'm'
    UPDATE_AUTH = 'U'


# Type aliases for instruction prefix unions
PlateReaderInstructionPrefixes = Union[
    GenericInstructionPrefixes,
    PlateReaderSpecificInstructionPrefixes
]


# ---------------- Responses -----------------------

class GenericResponsePrefixes(str, Enum):
    """Generic response prefixes for all devices"""
    CHILDREN = 'h'
    DEMO_REQ = 'u'
    FILE_LIST = 'f'
    GET_QC_MODE_KEY = 'K'
    INFO = 'i'
    SETTINGS = 'gP'
    STATUS = 'x'
    TEMPERATURE = 't'
    TIMESTAMP = 'Z'
    TURN_QC_MODE_OFF = 'xR'
    TURN_QC_MODE_ON = 'xQ'
    GET_FILE = 'F'
    LIST_EXPERIMENTS = 'e'
    GET_EXPERIMENT = 'E'
    DATA_TRANSMISSION = 'D'
    CMD_ERROR = '!'
    GET_STORAGE_MODIFIED_TIMESTAMP = 'm'
    FILE_STORAGE_OPERATION = 'f'
    BUTTON_CLICK = 'b'
    STOP = 's'


class PlateReaderSpecificResponsePrefixes(str, Enum):
    """Plate reader specific response prefixes"""
    READ_WELL = 'd'
    LEGACY_START = 'S'
    EXPERIMENT_SETUP = 'A'
    SET_WAVELENGTHS = 'v'
    CALIBRATE = 'c'
    IREF = 'j'


# Type aliases for response prefix unions
StratusResponsePrefixes = Union[
    GenericResponsePrefixes,
    PlateReaderSpecificResponsePrefixes
]


class StartCommandPrefixes(str, Enum):
    """Start command (A) sub-prefixes"""
    RESET = '0'  # Reset start command to defaults
    INTERVAL = 'i'  # Set measurement interval (seconds)
    DURATION = 'd'  # Set measurement duration (seconds)
    MODE = 'm'  # Set measurement mode (bitfield)
    NAME = 'n'  # Set experiment name
    EXPERIMENT_ID = 'I'  # Set experiment ID
    USER = 'U'  # Set user who started experiment
    TYPE = 't'  # Set experiment type
    QUEUE = 'q'  # Queue experiment instead of starting
    PLATE = 'P'
    EXECUTE = '.'  # Execute the start command


class PlateTemplateMetadataPrefixes(str, Enum):
    """Plate template metadata (A P M) sub-prefixes"""
    ROWS = 'R'  # Number of rows
    COLS = 'C'  # Number of columns
    DIAMETER = 'D'  # Well diameter (μm)
    HEIGHT = 'H'  # Well height (μm)
    VOLUME = 'V'  # Well volume (μL)
    TREATMENT = 'T'  # Plate treatment type
    BOTTOM = 'B'  # Well-bottom type
    LID = 'L'  # Plate lid type
    WELL_DETECTOR = 'W'  # Assign detector to well
    MANUFACTURER = 'M'  # Plate manufacturer
    MODEL = 'm'  # Plate model number
    TEMPLATE_NAME = 'n'  # Template name
    LAYOUT = 'G'  # plate layout file (the .plate file)


class PlateTemplatePrefixes(str, Enum):
    """Plate template (A P) sub-prefixes"""
    METADATA = 'M'  # Plate metadata commands
    LAYOUT = 'G'  # Add line to layout file
    WELLS = 'W'  # Add line to wells file (deprecated as of v6.6.0)


class PlateTreatmentType(str, Enum):
    """Plate treatment types"""
    UNKNOWN = ''  # Unknown/unspecified
    UNTREATED = 'u'  # Untreated
    TISSUE_CULTURE = 't'  # Tissue-culture treated


class WellBottomType(str, Enum):
    """Well bottom types"""
    UNKNOWN = ''  # Unknown/unspecified
    ROUND = 'r'  # Round bottom
    FLAT = 'f'  # Flat bottom


class PlateLidType(str, Enum):
    """Plate lid types"""
    UNKNOWN = ''  # Unknown/unspecified
    NONE = 'n'  # No lid
    LID = 'l'  # Standard lid
    PERMEABLE_MEMBRANE = 'm'  # Permeable membrane (e.g., Breathe-Easy)
    IMPERMEABLE_MEMBRANE = 'M'  # Impermeable membrane (e.g., PCR plastic)


class ExperimentType(Enum):
    """Experiment types"""
    DEFER_TO_DURATION = -1  # Let duration determine type
    ENDPOINT = 0  # Endpoint measurement
    KINETIC = 1  # Kinetic measurement
    SMART_ENDPOINT = 2  # Smart endpoint (v6.11.0+)
    IREF_SWEEP = 3  # IREF sweep 0-255 by 5 (v6.11.0+)
