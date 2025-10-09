# tests/test_experiment_builder.py
import pytest
from cerillo.cdcl import (
    ExperimentBuilder,
    PlateTemplateBuilder,
    FullExperimentBuilder,
    ExperimentType,
    PlateTreatmentType,
    WellBottomType,
    PlateLidType
)


class TestExperimentBuilder:
    """Test suite for ExperimentBuilder"""

    def test_simple_build(self):
        """Test building a simple experiment"""
        builder = ExperimentBuilder()
        commands = builder.set_interval(60).build()

        assert len(commands) == 1
        assert commands[0].raw_message == "A i 60"

    def test_chained_commands(self):
        """Test chaining multiple commands"""
        builder = ExperimentBuilder()
        commands = (builder
                    .reset()
                    .set_interval(60)
                    .set_duration(3600)
                    .set_name("Test")
                    .build())

        assert len(commands) == 4
        assert commands[0].raw_message == "A 0"
        assert commands[1].raw_message == "A i 60"
        assert commands[2].raw_message == "A d 3600"
        assert commands[3].raw_message == "A n Test"

    def test_experiment_types(self):
        """Test setting different experiment types"""
        builder = ExperimentBuilder()

        # Kinetic
        commands = builder.set_type(ExperimentType.KINETIC).build()
        assert commands[0].raw_message == "A t 1"

        builder.clear()

        # Endpoint
        commands = builder.set_type(ExperimentType.ENDPOINT).build()
        assert commands[0].raw_message == "A t 0"

    def test_queue_command(self):
        """Test queue command"""
        builder = ExperimentBuilder()

        # Queue = True
        commands = builder.set_queue(True).build()
        assert commands[0].raw_message == "A q 1"

        builder.clear()

        # Queue = False
        commands = builder.set_queue(False).build()
        assert commands[0].raw_message == "A q 0"

    def test_with_command_id(self):
        """Test using command IDs"""
        builder = ExperimentBuilder(command_id="test")
        commands = builder.set_interval(60).build()

        assert len(commands) == 1
        assert commands[0].command_id == "test"
        assert commands[0].raw_message == "A*test i 60"

    def test_build_messages(self):
        """Test build_messages returns raw strings"""
        builder = ExperimentBuilder()
        messages = (builder
                    .set_interval(60)
                    .set_duration(3600)
                    .build_messages())

        assert len(messages) == 4
        assert isinstance(messages[0], str)
        print(messages)
        assert messages[0] == 'A 0'
        assert messages[1] == "A i 60"
        assert messages[2] == "A d 3600"
        assert messages[3] == 'A .'

    def test_clear(self):
        """Test clearing builder"""
        builder = ExperimentBuilder()
        builder.set_interval(60).set_duration(3600)

        assert len(builder.build()) == 2

        builder.clear()
        assert len(builder.build()) == 0

    def test_user_command(self):
        """Test setting user"""
        builder = ExperimentBuilder()
        commands = builder.set_user("researcher@lab.com").build()

        assert commands[0].raw_message == "A U researcher@lab.com"

    def test_experiment_id(self):
        """Test setting experiment ID"""
        builder = ExperimentBuilder()
        commands = builder.set_experiment_id("uuid-1234").build()

        assert commands[0].raw_message == "A I uuid-1234"


class TestPlateTemplateBuilder:
    """Test suite for PlateTemplateBuilder"""

    def test_96_well_plate(self):
        """Test 96-well plate preset"""
        builder = PlateTemplateBuilder()
        commands = builder.set_96_well_plate().build()

        # Should set 5 parameters (rows, cols, diameter, height, volume)
        assert len(commands) == 5

        messages = [cmd.raw_message for cmd in commands]
        assert "A P M R 8" in messages
        assert "A P M C 12" in messages

    def test_6_well_plate(self):
        """Test 6-well plate preset"""
        builder = PlateTemplateBuilder()
        commands = builder.set_6_well_plate().build()

        messages = [cmd.raw_message for cmd in commands]
        assert "A P M R 2" in messages
        assert "A P M C 3" in messages

    def test_custom_dimensions(self):
        """Test setting custom dimensions"""
        builder = PlateTemplateBuilder()
        commands = (builder
                    .set_rows(4)
                    .set_cols(6)
                    .set_well_diameter(10000)
                    .build())

        assert len(commands) == 3
        assert commands[0].raw_message == "A P M R 4"
        assert commands[1].raw_message == "A P M C 6"
        assert commands[2].raw_message == "A P M D 10000"

    def test_treatment_types(self):
        """Test setting plate treatment"""
        builder = PlateTemplateBuilder()

        # Tissue culture treated
        commands = builder.set_tissue_culture_treated().build()
        assert commands[0].raw_message == "A P M T t"

        builder.clear()

        # Untreated
        commands = builder.set_untreated().build()
        assert commands[0].raw_message == "A P M T u"

    def test_bottom_types(self):
        """Test setting well bottom types"""
        builder = PlateTemplateBuilder()

        # Flat bottom
        commands = builder.set_flat_bottom().build()
        assert commands[0].raw_message == "A P M B f"

        builder.clear()

        # Round bottom
        commands = builder.set_round_bottom().build()
        assert commands[0].raw_message == "A P M B r"

    def test_lid_types(self):
        """Test setting lid types"""
        builder = PlateTemplateBuilder()

        # Standard lid
        commands = builder.set_standard_lid().build()
        assert commands[0].raw_message == "A P M L l"

        builder.clear()

        # No lid
        commands = builder.set_no_lid().build()
        assert commands[0].raw_message == "A P M L n"

        builder.clear()

        # Breathe-Easy
        commands = builder.set_breathe_easy().build()
        assert commands[0].raw_message == "A P M L m"

    def test_detector_assignment(self):
        """Test assigning detectors to wells"""
        builder = PlateTemplateBuilder()
        commands = builder.assign_detector_to_well(1, 0).build()

        assert len(commands) == 1
        assert commands[0].raw_message == "A P M W 1 0"

    def test_metadata(self):
        """Test setting plate metadata"""
        builder = PlateTemplateBuilder()
        commands = (builder
                    .set_manufacturer("Corning")
                    .set_model("3595")
                    .set_template_name("Test Plate")
                    .build())

        assert len(commands) == 3
        assert commands[0].raw_message == "A P M M Corning"
        assert commands[1].raw_message == "A P M m 3595"
        assert commands[2].raw_message == "A P M n Test Plate"

    def test_complete_plate_config(self):
        """Test complete plate configuration"""
        builder = PlateTemplateBuilder()
        messages = (builder
                    .set_96_well_plate()
                    .set_manufacturer("Corning")
                    .set_model("3595")
                    .set_flat_bottom()
                    .set_tissue_culture_treated()
                    .set_standard_lid()
                    .build_messages())

        assert len(messages) == 10
        assert "A P M R 8" in messages
        assert "A P M C 12" in messages
        assert "A P M M Corning" in messages
        assert "A P M m 3595" in messages
        assert "A P M B f" in messages
        assert "A P M T t" in messages
        assert "A P M L l" in messages


class TestFullExperimentBuilder:
    """Test suite for FullExperimentBuilder"""

    def test_experiment_and_plate(self):
        """Test building both experiment and plate"""
        builder = FullExperimentBuilder()

        builder.plate().set_96_well_plate()
        builder.experiment().set_interval(60)

        commands = builder.build_all()

        # Should have plate commands first, then experiment commands
        assert len(commands) > 5

        # First commands should be plate template (A P M ...)
        messages = [cmd.raw_message for cmd in commands]
        plate_msgs = [m for m in messages if m.startswith("A P")]
        exp_msgs = [m for m in messages if m.startswith("A i")]

        assert len(plate_msgs) == 5  # 96-well preset has 5 commands
        assert len(exp_msgs) == 1

    def test_build_all_messages(self):
        """Test building all messages as strings"""
        builder = FullExperimentBuilder()

        builder.plate().set_96_well_plate()
        builder.experiment().set_interval(60)

        messages = builder.build_all_messages()

        assert len(messages) == 8  # 5 plate + 3 experiment
        assert all(isinstance(m, str) for m in messages)

    def test_switching_contexts(self):
        """Test switching between plate and experiment contexts"""
        builder = FullExperimentBuilder()

        # Configure plate
        plate_builder = builder.plate()
        plate_builder.set_96_well_plate()

        # Switch to experiment
        exp_builder = builder.experiment()
        exp_builder.set_interval(60)

        # Switch back to plate
        plate_builder2 = builder.plate()
        plate_builder2.set_manufacturer("Test")

        # Should be same builder
        assert plate_builder is plate_builder2

        commands = builder.build_all()
        assert len(commands) == 7  # 5 + 1 plate, 1 experiment

    def test_complete_workflow(self):
        """Test a complete experiment setup workflow"""
        builder = FullExperimentBuilder(command_id="test")

        # Configure plate template
        builder.plate().set_96_well_plate()
        builder.plate().set_manufacturer("Greiner")
        builder.plate().set_model("655101")
        builder.plate().set_flat_bottom()
        builder.plate().set_tissue_culture_treated()

        # Configure experiment
        builder.experiment().set_name("Growth Curve")
        builder.experiment().set_user("scientist@lab.com")
        builder.experiment().set_interval(300)
        builder.experiment().set_duration(86400)
        builder.experiment().set_type(ExperimentType.KINETIC)

        messages = builder.build_all_messages()
        print(messages)

        # Check that all commands have the command ID
        assert all("*test " in m for m in messages)

        # Check we have both plate and experiment commands
        plate_count = sum(1 for m in messages if "A*test P M" in m)
        exp_count = sum(1 for m in messages if m.startswith(
            "A*test") and "P" not in m)

        assert plate_count == 9
        assert exp_count == 7   # reset + 5 settings + execute


class TestBuilderEdgeCases:
    """Test edge cases and error conditions"""

    def test_empty_builder(self):
        """Test building with no commands"""
        builder = ExperimentBuilder()
        commands = builder.build()

        assert len(commands) == 0
        assert commands == []

    def test_multiple_builds(self):
        """Test that build() doesn't clear commands"""
        builder = ExperimentBuilder()
        builder.set_interval(60)

        commands1 = builder.build()
        commands2 = builder.build()

        assert len(commands1) == 1
        assert len(commands2) == 1
        assert commands1[0].raw_message == commands2[0].raw_message

    def test_build_returns_copy(self):
        """Test that build() returns a copy of commands"""
        builder = ExperimentBuilder()
        builder.set_interval(60)

        commands1 = builder.build()
        commands2 = builder.build()

        # Should be different list objects
        assert commands1 is not commands2

        # But contain equivalent commands
        assert len(commands1) == len(commands2)

    def test_infinite_duration(self):
        """Test setting infinite duration"""
        builder = ExperimentBuilder()
        commands = builder.set_duration(-1).build()

        assert commands[0].raw_message == "A d -1"

    def test_empty_name(self):
        """Test empty experiment name (auto-generate)"""
        builder = ExperimentBuilder()
        commands = builder.set_name("").build()

        # Should still create command but without name parameter
        assert commands[0].raw_message == "A n"

    def test_empty_experiment_id(self):
        """Test empty experiment ID (auto-generate)"""
        builder = ExperimentBuilder()
        commands = builder.set_experiment_id("").build()

        assert commands[0].raw_message == "A I"

    def test_detector_assignment_multiple_wells(self):
        """Test assigning multiple detectors to wells"""
        builder = PlateTemplateBuilder()

        # Assign 3 detectors to 3 wells
        for i in range(3):
            builder.assign_detector_to_well(i + 1, i)

        commands = builder.build()
        assert len(commands) == 3

        messages = [cmd.raw_message for cmd in commands]
        assert "A P M W 1 0" in messages
        assert "A P M W 2 1" in messages
        assert "A P M W 3 2" in messages


class TestBuilderIntegration:
    """Integration tests with realistic scenarios"""

    def test_kinetic_growth_curve(self):
        """Test setting up a typical bacterial growth curve"""
        builder = FullExperimentBuilder()
        (builder
            .experiment()
            .reset()
            .set_name("E. coli Growth Curve")
            .set_user("microbiologist@lab.edu")
            .set_interval(600)      # 10 minutes
            .set_duration(43200)    # 12 hours
            .set_type(ExperimentType.KINETIC)
         )

        (builder
         .plate()
         .set_96_well_plate()
         .set_manufacturer("Corning")
         .set_flat_bottom()
         .set_tissue_culture_treated())
        builder.experiment()

        messages = (
            builder.build_all_messages())

        assert len(messages) > 10
        assert any("Growth Curve" in m for m in messages)
        assert any("A t 1" in m for m in messages)  # Kinetic type

    def test_endpoint_elisa(self):
        """Test setting up an ELISA endpoint read"""
        builder = FullExperimentBuilder()

        builder.plate().set_96_well_plate().set_manufacturer("Thermo").set_flat_bottom()
        builder.experiment().reset().set_name("ELISA Plate 1").set_type(
            ExperimentType.ENDPOINT)
        messages = (builder.build_all_messages())

        assert any("ELISA" in m for m in messages)
        assert any("A t 0" in m for m in messages)  # Endpoint type

    def test_6_well_cell_culture(self):
        """Test 6-well plate for cell culture"""
        builder = FullExperimentBuilder()

        # Build plate with detector assignments
        plate = builder.plate()
        plate.set_6_well_plate()
        plate.set_tissue_culture_treated()

        # Assign detectors (example: 4 detectors per well for 6 wells)
        for well in range(6):
            for detector in range(4):
                plate.assign_detector_to_well(
                    detector_num=well * 4 + detector + 1,
                    well_num=well
                )

        messages = builder.build_all_messages()

        # Should have 6-well config + 24 detector assignments
        detector_msgs = [m for m in messages if "A P M W" in m]
        assert len(detector_msgs) == 24


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
