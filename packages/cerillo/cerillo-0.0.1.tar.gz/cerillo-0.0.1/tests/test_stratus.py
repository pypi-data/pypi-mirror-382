import pytest
from cerillo import StratusReader
from cerillo.cdcl import FullExperimentBuilder, ExperimentType


class TestStratusSimulation:
    """Test suite for Stratus reader in simulation mode"""

    def test_initialization(self):
        """Test that Stratus reader initializes correctly in simulation mode"""
        reader = StratusReader(simulate=True)
        reader.connect()
        assert reader.simulate is True
        assert reader.plate_type == "96-well"
        reader.disconnect()

    def test_real_stratus(self):
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
        reader = StratusReader(port="/dev/ttyUSB0")
        reader.connect()
        reader.start_experiment(builder)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
