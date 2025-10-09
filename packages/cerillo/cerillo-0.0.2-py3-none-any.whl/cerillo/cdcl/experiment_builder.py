# src/opentrons_plate_reader/experiment_builder.py
"""
Builder classes for constructing Stratus experiments with fluent API
"""

from typing import Optional, List, Tuple
from dataclasses import dataclass, field
from .cdcl import CDCLCommand
from .start_commands import (
    ResetStartCommand,
    SetIntervalCommand,
    SetDurationCommand,
    SetModeCommand,
    SetExperimentNameCommand,
    SetExperimentIDCommand,
    SetUserCommand,
    SetExperimentTypeCommand,
    SetQueueCommand,
    ExecuteStartCommand,
    SetPlateRowsCommand,
    SetPlateColsCommand,
    SetWellDiameterCommand,
    SetWellHeightCommand,
    SetWellVolumeCommand,
    SetPlateTreatmentCommand,
    SetWellBottomCommand,
    SetPlateLidCommand,
    AssignDetectorToWellCommand,
    SetPlateManufacturerCommand,
    SetPlateModelCommand,
    SetPlateTemplateNameCommand, AddPlateLayoutLineCommand
)
from .prefixes import (
    ExperimentType,
    PlateTreatmentType,
    WellBottomType,
    PlateLidType
)


class ExperimentBuilder:
    """
    Fluent builder for constructing Stratus experiment configurations.

    Example:
        builder = ExperimentBuilder()
        commands = (builder
            .reset()
            .set_interval(60)
            .set_duration(3600)
            .set_name("My Experiment")
            .set_user("researcher@lab.com")
            .set_type(ExperimentType.KINETIC)
            .build())
    """

    def __init__(self, command_id: Optional[str] = None):
        """
        Initialize experiment builder.

        Args:
            command_id: Optional command ID to use for all commands
        """
        self._commands: List[CDCLCommand] = []
        self._command_id = command_id

    def reset(self) -> 'ExperimentBuilder':
        """Reset start command to defaults"""
        cmd = ResetStartCommand(command_id=self._command_id)
        self._commands.append(cmd)
        return self

    def set_interval(self, interval: int) -> 'ExperimentBuilder':
        """
        Set measurement interval in seconds.

        Args:
            interval: Interval in seconds (-1 to ignore)
        """
        cmd = SetIntervalCommand(
            interval=interval, command_id=self._command_id)
        self._commands.append(cmd)
        return self

    def set_duration(self, duration: int) -> 'ExperimentBuilder':
        """
        Set measurement duration in seconds.

        Args:
            duration: Duration in seconds (-1 for infinite)
        """
        cmd = SetDurationCommand(
            duration=duration, command_id=self._command_id)
        self._commands.append(cmd)
        return self

    def set_mode(self, mode: int) -> 'ExperimentBuilder':
        """
        Set measurement mode bitfield.

        Args:
            mode: Mode bitfield value
        """
        cmd = SetModeCommand(mode=mode, command_id=self._command_id)
        self._commands.append(cmd)
        return self

    def set_name(self, name: str) -> 'ExperimentBuilder':
        """
        Set experiment name.

        Args:
            name: Experiment name (empty to auto-generate)
        """
        cmd = SetExperimentNameCommand(name=name, command_id=self._command_id)
        self._commands.append(cmd)
        return self

    def set_experiment_id(self, experiment_id: str) -> 'ExperimentBuilder':
        """
        Set experiment ID.

        Args:
            experiment_id: UUID v4 string (empty to auto-generate)
        """
        cmd = SetExperimentIDCommand(
            experiment_id=experiment_id,
            command_id=self._command_id
        )
        self._commands.append(cmd)
        return self

    def set_user(self, user: str) -> 'ExperimentBuilder':
        """
        Set user who started the experiment.

        Args:
            user: User identifier (max 64 characters)
        """
        cmd = SetUserCommand(user=user, command_id=self._command_id)
        self._commands.append(cmd)
        return self

    def set_type(self, exp_type: ExperimentType) -> 'ExperimentBuilder':
        """
        Set experiment type.

        Args:
            exp_type: ExperimentType enum value
        """
        cmd = SetExperimentTypeCommand(
            exp_type=exp_type, command_id=self._command_id)
        self._commands.append(cmd)
        return self

    def set_queue(self, queue: bool = True) -> 'ExperimentBuilder':
        """
        Set whether to queue the experiment.

        Args:
            queue: True to queue, False to start immediately
        """
        cmd = SetQueueCommand(queue=queue, command_id=self._command_id)
        self._commands.append(cmd)
        return self

    def build(self) -> List[CDCLCommand]:
        """
        Build and return the list of commands.

        Returns:
            List of CDCLCommand objects ready to send
        """
        return self._commands.copy()

    def build_messages(self) -> List[str]:
        """
        Build and return raw message strings.

        Returns:
            List of raw CDCL message strings
        """
        # Make a shallow copy so we don't mutate internal state
        commands = self._commands.copy()

        # Ensure experiment commands include a reset at the start for safety
        if not any(isinstance(c, ResetStartCommand) for c in commands):
            commands = [ResetStartCommand(
                command_id=self._command_id)] + commands

        # Ensure an execute is present at the end so messages built via this
        # convenience method will start the experiment automatically.
        if not isinstance(commands[len(commands)-1], ExecuteStartCommand):
            commands = commands + \
                [ExecuteStartCommand(
                    command_id=self._command_id)]

        return [cmd.raw_message for cmd in commands]

    def clear(self) -> 'ExperimentBuilder':
        """Clear all commands from the builder"""
        self._commands.clear()
        return self


class PlateTemplateBuilder:
    """
    Fluent builder for constructing plate templates.

    Example:
        builder = PlateTemplateBuilder()
        commands = (builder
            .set_96_well_plate()
            .set_manufacturer("Corning")
            .set_model("3595")
            .set_flat_bottom()
            .set_tissue_culture_treated()
            .build())
    """

    def __init__(self, command_id: Optional[str] = None):
        """
        Initialize plate template builder.

        Args:
            command_id: Optional command ID to use for all commands
        """
        self._commands: List[CDCLCommand] = []
        self._command_id = command_id

    def set_rows(self, rows: int) -> 'PlateTemplateBuilder':
        """Set number of rows"""
        cmd = SetPlateRowsCommand(rows=rows, command_id=self._command_id)
        self._commands.append(cmd)
        return self

    def set_cols(self, cols: int) -> 'PlateTemplateBuilder':
        """Set number of columns"""
        cmd = SetPlateColsCommand(cols=cols, command_id=self._command_id)
        self._commands.append(cmd)
        return self

    def set_well_diameter(self, diameter_um: int) -> 'PlateTemplateBuilder':
        """Set well diameter in microns"""
        cmd = SetWellDiameterCommand(
            diameter_um=diameter_um, command_id=self._command_id)
        self._commands.append(cmd)
        return self

    def set_well_height(self, height_um: int) -> 'PlateTemplateBuilder':
        """Set well height in microns"""
        cmd = SetWellHeightCommand(
            height_um=height_um, command_id=self._command_id)
        self._commands.append(cmd)
        return self

    def set_well_volume(self, volume_ul: int) -> 'PlateTemplateBuilder':
        """Set well volume in microliters"""
        cmd = SetWellVolumeCommand(
            volume_ul=volume_ul, command_id=self._command_id)
        self._commands.append(cmd)
        return self

    def set_treatment(self, treatment: PlateTreatmentType) -> 'PlateTemplateBuilder':
        """Set plate treatment type"""
        cmd = SetPlateTreatmentCommand(
            treatment=treatment, command_id=self._command_id)
        self._commands.append(cmd)
        return self

    def set_tissue_culture_treated(self) -> 'PlateTemplateBuilder':
        """Set plate as tissue-culture treated"""
        return self.set_treatment(PlateTreatmentType.TISSUE_CULTURE)

    def set_untreated(self) -> 'PlateTemplateBuilder':
        """Set plate as untreated"""
        return self.set_treatment(PlateTreatmentType.UNTREATED)

    def set_bottom_type(self, bottom: WellBottomType) -> 'PlateTemplateBuilder':
        """Set well bottom type"""
        cmd = SetWellBottomCommand(bottom=bottom, command_id=self._command_id)
        self._commands.append(cmd)
        return self

    def set_flat_bottom(self) -> 'PlateTemplateBuilder':
        """Set wells as flat-bottom"""
        return self.set_bottom_type(WellBottomType.FLAT)

    def set_round_bottom(self) -> 'PlateTemplateBuilder':
        """Set wells as round-bottom"""
        return self.set_bottom_type(WellBottomType.ROUND)

    def set_lid_type(self, lid: PlateLidType) -> 'PlateTemplateBuilder':
        """Set plate lid type"""
        cmd = SetPlateLidCommand(lid=lid, command_id=self._command_id)
        self._commands.append(cmd)
        return self

    def set_standard_lid(self) -> 'PlateTemplateBuilder':
        """Set standard lid"""
        return self.set_lid_type(PlateLidType.LID)

    def set_no_lid(self) -> 'PlateTemplateBuilder':
        """Set no lid"""
        return self.set_lid_type(PlateLidType.NONE)

    def set_breathe_easy(self) -> 'PlateTemplateBuilder':
        """Set permeable membrane (e.g., Breathe-Easy)"""
        return self.set_lid_type(PlateLidType.PERMEABLE_MEMBRANE)

    def assign_detector_to_well(
        self,
        detector_num: int,
        well_num: int
    ) -> 'PlateTemplateBuilder':
        """
        Assign a detector to measure a specific well.

        Args:
            detector_num: Detector number
            well_num: Well number
        """
        cmd = AssignDetectorToWellCommand(
            detector_num=detector_num,
            well_num=well_num,
            command_id=self._command_id
        )
        self._commands.append(cmd)
        return self

    def set_manufacturer(self, manufacturer: str) -> 'PlateTemplateBuilder':
        """Set plate manufacturer"""
        cmd = SetPlateManufacturerCommand(
            manufacturer=manufacturer,
            command_id=self._command_id
        )
        self._commands.append(cmd)
        return self

    def set_model(self, model: str) -> 'PlateTemplateBuilder':
        """Set plate model number"""
        cmd = SetPlateModelCommand(model=model, command_id=self._command_id)
        self._commands.append(cmd)
        return self

    def set_template_name(self, name: str) -> 'PlateTemplateBuilder':
        """Set plate template name"""
        cmd = SetPlateTemplateNameCommand(
            name=name, command_id=self._command_id)
        self._commands.append(cmd)
        return self

    def add_plate_layout_line(self, line: str) -> 'PlateTemplateBuilder':
        """Add to plate layout file"""
        cmd = AddPlateLayoutLineCommand(line=line, command_id=self._command_id)
        self._commands.append(cmd)
        return self

    # Convenience methods for common plate types
    def set_96_well_plate(self) -> 'PlateTemplateBuilder':
        """Configure as standard 96-well plate"""
        return (self
                .set_rows(8)
                .set_cols(12)
                .set_well_diameter(6400)
                .set_well_height(10900)
                .set_well_volume(200))

    def set_24_well_plate(self) -> 'PlateTemplateBuilder':
        """Configure as standard 24-well plate"""
        return (self
                .set_rows(4)
                .set_cols(6)
                .set_well_diameter(15500)
                .set_well_height(17400)
                .set_well_volume(340))

    def set_6_well_plate(self) -> 'PlateTemplateBuilder':
        """Configure as standard 6-well plate"""
        return (self
                .set_rows(2)
                .set_cols(3)
                .set_well_diameter(35000)
                .set_well_height(18500)
                .set_well_volume(1500))

    def set_12_well_plate(self) -> 'PlateTemplateBuilder':
        """Configure as standard 12-well plate"""
        return (self
                .set_rows(3)
                .set_cols(4)
                .set_well_diameter(22800)
                .set_well_height(17000)
                .set_well_volume(852))

    def build(self) -> List[CDCLCommand]:
        """
        Build and return the list of commands.

        Returns:
            List of CDCLCommand objects ready to send
        """
        return self._commands.copy()

    def build_messages(self) -> List[str]:
        """
        Build and return raw message strings.

        Returns:
            List of raw CDCL message strings
        """
        return [cmd.raw_message for cmd in self._commands]

    def clear(self) -> 'PlateTemplateBuilder':
        """Clear all commands from the builder"""
        self._commands.clear()
        return self


class FullExperimentBuilder:
    """
    Combined builder for both experiment settings and plate template.

    Example:
        builder = FullExperimentBuilder()
        builder
            .experiment()
                .set_name("Growth Curve")
                .set_interval(300)
                .set_duration(86400)
            builder
            .plate()
                .set_96_well_plate()
                .set_manufacturer("Corning")
            commands = builder.build_all()
    """

    def __init__(self, command_id: Optional[str] = None):
        """
        Initialize full experiment builder.

        Args:
            command_id: Optional command ID to use for all commands
        """
        self._experiment_builder = ExperimentBuilder(command_id)
        self._plate_builder = PlateTemplateBuilder(command_id)
        self._current_builder = self._experiment_builder

    def experiment(self) -> ExperimentBuilder:
        """
        Switch to experiment configuration.

        Returns:
            ExperimentBuilder for chaining
        """
        self._current_builder = self._experiment_builder
        return self._experiment_builder

    def plate(self) -> PlateTemplateBuilder:
        """
        Switch to plate template configuration.

        Returns:
            PlateTemplateBuilder for chaining
        """
        self._current_builder = self._plate_builder
        return self._plate_builder

    def build_all(self) -> List[CDCLCommand]:
        """
        Build all commands (plate template first, then experiment).

        Returns:
            Combined list of all commands
        """
        plate_commands = self._plate_builder.build()
        exp_commands = self._experiment_builder.build()
        full_commands = exp_commands + plate_commands

        # Ensure experiment commands include a reset at the start for safety
        if not any(isinstance(c, ResetStartCommand) for c in exp_commands):
            exp_commands = [ResetStartCommand(
                command_id=self._experiment_builder._command_id)] + exp_commands

        if not isinstance(full_commands[len(full_commands)-1], ExecuteStartCommand):
            full_commands = full_commands + \
                [ExecuteStartCommand(
                    command_id=self._experiment_builder._command_id)]
        return full_commands

    def build_all_messages(self) -> List[str]:
        """
        Build all raw message strings.

        Returns:
            Combined list of all message strings
        """
        # Build command objects but avoid mutating the builders' internal lists
        full_commands = self.build_all()

        # Ensure an execute is present at the end so messages built via this
        # convenience method will start the experiment automatically.
        return [cmd.raw_message for cmd in full_commands]
