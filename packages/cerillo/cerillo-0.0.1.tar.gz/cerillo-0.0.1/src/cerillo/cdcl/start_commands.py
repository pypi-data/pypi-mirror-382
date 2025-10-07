# src/opentrons_plate_reader/start_commands.py
"""Helper classes for building PLate Reader start commands"""

from dataclasses import dataclass, field
from typing import Optional, List
from .cdcl import CDCLCommand
from .prefixes import (
    StartCommandPrefixes,
    PlateTemplateMetadataPrefixes,
    PlateTemplatePrefixes,
    PlateTreatmentType,
    WellBottomType,
    PlateLidType,
    ExperimentType
)


@dataclass
class StartCommand(CDCLCommand):
    """Base start command (A prefix)"""
    command: str = field(default="A", init=False)
    command_id: Optional[str] = None
    params: Optional[List[str]] = None

    def __post_init__(self):
        if self.params is None:
            self.params = []
        super().__post_init__()


@dataclass
class ResetStartCommand(StartCommand):
    """Reset start command to defaults (A 0 or A R)"""

    def __post_init__(self):
        self.params = [StartCommandPrefixes.RESET.value]
        super().__post_init__()


@dataclass
class SetIntervalCommand(StartCommand):
    """Set measurement interval in seconds (A i <interval>)"""
    interval: int = 300  # 5 minutes

    def __post_init__(self):
        self.params = [StartCommandPrefixes.INTERVAL.value, str(self.interval)]
        super().__post_init__()


@dataclass
class SetDurationCommand(StartCommand):
    """Set measurement duration in seconds (A d <duration>)"""
    duration: int = -1  # -1 for infinite

    def __post_init__(self):
        self.params = [StartCommandPrefixes.DURATION.value, str(self.duration)]
        super().__post_init__()


@dataclass
class SetModeCommand(StartCommand):
    """Set measurement mode bitfield (A m <mode>)"""
    mode: int = 0

    def __post_init__(self):
        self.params = [StartCommandPrefixes.MODE.value, str(self.mode)]
        super().__post_init__()


@dataclass
class SetExperimentNameCommand(StartCommand):
    """Set experiment name (A n <name>)"""
    name: str = ""  # Empty to auto-generate

    def __post_init__(self):
        if self.name:
            self.params = [StartCommandPrefixes.NAME.value, self.name]
        else:
            self.params = [StartCommandPrefixes.NAME.value]
        super().__post_init__()


@dataclass
class SetExperimentIDCommand(StartCommand):
    """Set experiment ID (A I <ID>)"""
    experiment_id: str = ""  # Empty to auto-generate

    def __post_init__(self):
        if self.experiment_id:
            self.params = [
                StartCommandPrefixes.EXPERIMENT_ID.value, self.experiment_id]
        else:
            self.params = [StartCommandPrefixes.EXPERIMENT_ID.value]
        super().__post_init__()


@dataclass
class SetUserCommand(StartCommand):
    """Set user who started experiment (A U <user>)"""
    user: str = ""

    def __post_init__(self):
        self.params = [StartCommandPrefixes.USER.value, self.user]
        super().__post_init__()


@dataclass
class SetExperimentTypeCommand(StartCommand):
    """Set experiment type (A t <type>)"""
    exp_type: ExperimentType = ExperimentType.ENDPOINT

    def __post_init__(self):
        self.params = [StartCommandPrefixes.TYPE.value,
                       str(self.exp_type.value)]
        super().__post_init__()


@dataclass
class SetQueueCommand(StartCommand):
    """Set whether to queue experiment (A q <0|1>)"""
    queue: bool = False

    def __post_init__(self):
        self.params = [StartCommandPrefixes.QUEUE.value,
                       "1" if self.queue else "0"]
        super().__post_init__()


@dataclass
class ExecuteStartCommand(StartCommand):
    """Execute the start command (A .)"""

    def __post_init__(self):
        self.params = [StartCommandPrefixes.EXECUTE.value]
        super().__post_init__()


# Plate template commands

@dataclass
class PlateTemplateCommand(CDCLCommand):
    """Base plate template command (A P prefix)"""
    command: str = field(default="A", init=False)
    command_id: Optional[str] = None
    params: Optional[List[str]] = None

    def __post_init__(self):
        if self.params is None:
            self.params = []
        super().__post_init__()


@dataclass
class SetPlateRowsCommand(PlateTemplateCommand):
    """Set number of rows (A P M R <rows>)"""
    rows: int = 8

    def __post_init__(self):
        self.params = [
            StartCommandPrefixes.PLATE.value + PlateTemplatePrefixes.METADATA.value +
            PlateTemplateMetadataPrefixes.ROWS.value,
            str(self.rows)
        ]
        super().__post_init__()


@dataclass
class SetPlateColsCommand(PlateTemplateCommand):
    """Set number of columns (A P M C <cols>)"""
    cols: int = 12

    def __post_init__(self):
        self.params = [
            StartCommandPrefixes.PLATE.value + PlateTemplatePrefixes.METADATA.value +
            PlateTemplateMetadataPrefixes.COLS.value,
            str(self.cols)
        ]
        super().__post_init__()


@dataclass
class SetWellDiameterCommand(PlateTemplateCommand):
    """Set well diameter in microns (A P M D <diameter>)"""
    diameter_um: int = 6400  # Default for 96-well

    def __post_init__(self):
        self.params = [
            StartCommandPrefixes.PLATE.value + PlateTemplatePrefixes.METADATA.value +
            PlateTemplateMetadataPrefixes.DIAMETER.value,
            str(self.diameter_um)
        ]
        super().__post_init__()


@dataclass
class SetWellHeightCommand(PlateTemplateCommand):
    """Set well height in microns (A P M H <height>)"""
    height_um: int = 10900  # Default for 96-well

    def __post_init__(self):
        self.params = [
            StartCommandPrefixes.PLATE.value + PlateTemplatePrefixes.METADATA.value +
            PlateTemplateMetadataPrefixes.HEIGHT.value,
            str(self.height_um)
        ]
        super().__post_init__()


@dataclass
class SetWellVolumeCommand(PlateTemplateCommand):
    """Set well volume in microliters (A P M V <volume>)"""
    volume_ul: int = 360  # Default for 96-well

    def __post_init__(self):
        self.params = [
            StartCommandPrefixes.PLATE.value + PlateTemplatePrefixes.METADATA.value +
            PlateTemplateMetadataPrefixes.VOLUME.value,
            str(self.volume_ul)
        ]
        super().__post_init__()


@dataclass
class SetPlateTreatmentCommand(PlateTemplateCommand):
    """Set plate treatment type (A P M T <type>)"""
    treatment: PlateTreatmentType = PlateTreatmentType.UNKNOWN

    def __post_init__(self):
        self.params = [
            StartCommandPrefixes.PLATE.value + PlateTemplatePrefixes.METADATA.value +
            PlateTemplateMetadataPrefixes.TREATMENT.value,
            self.treatment.value
        ]
        super().__post_init__()


@dataclass
class SetWellBottomCommand(PlateTemplateCommand):
    """Set well bottom type (A P M B <type>)"""
    bottom: WellBottomType = WellBottomType.UNKNOWN

    def __post_init__(self):
        self.params = [
            StartCommandPrefixes.PLATE.value + PlateTemplatePrefixes.METADATA.value +
            PlateTemplateMetadataPrefixes.BOTTOM.value,
            self.bottom.value
        ]
        super().__post_init__()


@dataclass
class SetPlateLidCommand(PlateTemplateCommand):
    """Set plate lid type (A P M L <type>)"""
    lid: PlateLidType = PlateLidType.UNKNOWN

    def __post_init__(self):
        self.params = [
            StartCommandPrefixes.PLATE.value + PlateTemplatePrefixes.METADATA.value +
            PlateTemplateMetadataPrefixes.LID.value,
            self.lid.value
        ]
        super().__post_init__()


@dataclass
class AssignDetectorToWellCommand(PlateTemplateCommand):
    """Assign detector to well (A P M W <detector> <well>)"""
    detector_num: int = 0
    well_num: int = 0

    def __post_init__(self):
        self.params = [
            StartCommandPrefixes.PLATE.value + PlateTemplatePrefixes.METADATA.value +
            PlateTemplateMetadataPrefixes.WELL_DETECTOR.value,
            str(self.detector_num),
            str(self.well_num)
        ]
        super().__post_init__()


@dataclass
class SetPlateManufacturerCommand(PlateTemplateCommand):
    """Set plate manufacturer (A P M M <manufacturer>)"""
    manufacturer: str = ""

    def __post_init__(self):
        self.params = [
            StartCommandPrefixes.PLATE.value + PlateTemplatePrefixes.METADATA.value +
            PlateTemplateMetadataPrefixes.MANUFACTURER.value,
            self.manufacturer
        ]
        super().__post_init__()


@dataclass
class SetPlateModelCommand(PlateTemplateCommand):
    """Set plate model number (A P M m <model>)"""
    model: str = ""

    def __post_init__(self):
        self.params = [
            StartCommandPrefixes.PLATE.value + PlateTemplatePrefixes.METADATA.value +
            PlateTemplateMetadataPrefixes.MODEL.value,
            self.model
        ]
        super().__post_init__()


@dataclass
class SetPlateTemplateNameCommand(PlateTemplateCommand):
    """Set plate template name (A P M n <name>)"""
    name: str = ""

    def __post_init__(self):
        self.params = [
            StartCommandPrefixes.PLATE.value + PlateTemplatePrefixes.METADATA.value +
            PlateTemplateMetadataPrefixes.TEMPLATE_NAME.value,
            self.name
        ]
        super().__post_init__()


@dataclass
class AddPlateLayoutLineCommand(PlateTemplateCommand):
    """Add to plate layout file (A P G <line>)"""
    line: str = ""

    def __post_init__(self):
        self.params = [
            PlateTemplateMetadataPrefixes.LAYOUT.value,
            self.line
        ]
        super().__post_init__()
