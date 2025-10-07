import pytest
from cerillo import RayoReader, MotorStepCommand


class TestRayoSimulation:
    """Test suite for Stratus reader in simulation mode"""

    def test_initialization(self):
        """Test that Stratus reader initializes correctly in simulation mode"""
        reader = RayoReader(simulate=True, has_motor=True)
        reader.connect()
        assert reader.simulate is True
        step_command = MotorStepCommand(steps=100)
        reader.move_motor(step_command)
        reader.disconnect()

    def test_real_rayo(self):
        """Test a complete experiment setup workflow"""

        # Configure plate template
        reader = RayoReader(port="/dev/ttyACM0", has_motor=True)
        reader.connect()
        reader.open_lid()
        reader.close_lid()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
