from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import serial
import string
import random
import time
from .cdcl.cdcl import CDCLCommand, CDCLParser, CDCLResponse, PlateReaderModeCalculator
from .cdcl.experiment_builder import FullExperimentBuilder
from .cdcl.prefixes import PlateReaderSpecificInstructionPrefixes, GenericInstructionPrefixes, StartCommandPrefixes, GenericResponsePrefixes
from operator import attrgetter


class CerilloBasePlateReader(ABC):
    """Base class for all Cerillo plate readers"""

    def __init__(self, port: str = '/dev/ttyUSB0', baudrate: int = 250000,
                 timeout: float = 120.0, simulate: bool = False):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.simulate = simulate
        self._connection: Optional[serial.Serial] = None
        self.serial_number = None
        self.model_number = None
        self.name = None
        self.status = None
        self.firmware_version = None
        self.wavelengths: List[int] = []

    def __repr__(self):
        """Developer-friendly representation"""
        conn_status = "connected" if self._connection and self._connection.is_open else "disconnected"
        sim_str = " [SIMULATION]" if self.simulate else ""

        # Basic info always shown
        parts = [f"{self.__class__.__name__}("]

        # Device info if available
        if self.name:
            parts.append(f"name='{self.name}'")
        if self.serial_number:
            parts.append(f"serial={self.serial_number}")
        if self.model_number:
            parts.append(f"model='{self.model_number}'")
        parts.append(f"wavelengths={self.wavelengths}")

        # Connection info
        parts.append(f"port='{self.port}'")
        parts.append(f"status={conn_status}{sim_str}")
        return ", ".join(parts) + ")"

    def connect(self) -> None:
        """Establish connection to the plate reader"""
        if self.simulate:
            print(f"[SIMULATION] Connected to {self.__class__.__name__}")
            self.serial_number = "12345"
            return

        try:
            self._connection = serial.Serial(
                self.port,
                self.baudrate,
                timeout=self.timeout
            )

            start_time = time.time()
            while (self.serial_number == None):
                # Check if timeout exceeded
                elapsed = time.time() - start_time
                if elapsed > self.timeout:
                    raise TimeoutError(
                        f"Device startup timed out after {self.timeout} seconds waiting for serial number line")

                line = self._connection.readline().decode().strip()
                print(line)
                if (line.startswith(":")):
                    self.serial_number = line[1:line.find(" ")]
                    print(
                        f"Connected to device with serial number {self.serial_number}")

            self.initialize()
        except serial.SerialException as e:
            raise ConnectionError(f"Failed to connect to plate reader: {e}")

    def disconnect(self) -> None:
        """Close connection to the plate reader"""
        if self.simulate:
            print(f"[SIMULATION] Disconnected from {self.__class__.__name__}")
            return

        if self._connection and self._connection.is_open:
            self._connection.close()

    def send_command(self, command: CDCLCommand, timeout: int = None) -> CDCLResponse:
        """Send command and return response"""
        # set timeout to classes if not passed
        if timeout == None:
            timeout = self.timeout
        try:

            # Add command ID if needed
            command_id = command.command_id
            if (not command.command_id or command.command_id == ""):
                command_id = ''.join(random.choice(
                    string.ascii_uppercase + string.digits) for _ in range(4))
                command.command_id = command_id
            # Send command (adjust formatting for your device)
            device_command = f"{command.to_message()}\n".encode()
            self.log_serial(direction="send", message=device_command)

            # return early if simulating
            if self.simulate:
                return

            if not self._connection or not self._connection.is_open:
                self.connect()

            # Clear any buffered input before sending command
            self._connection.reset_input_buffer()

            self._connection.write(device_command)
            self._connection.flush()
            # Read response (adjust based on your protocol)
            # clear echo
            response = ''
            echo = 0
            start_time = time.time()
            while (response == ''):
                # Check if timeout exceeded
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    raise TimeoutError(
                        f"Command {command} timed out after {timeout} seconds waiting for response with ID {command_id}")

                line = self._connection.readline().decode().strip()
                self.log_serial(direction="receive", message=line)
                # print(line)
                if (command_id in line):
                    # clear the echo
                    if (not echo):
                        echo = 1
                    else:
                        response = line
            print(f"$Command: {command} | $Response: {response}")

            if not CDCLParser.is_cdcl_response(response):
                raise TypeError(
                    "response is not a valid CDCL response", response)
            response = CDCLParser.parse_response(response)

            return response
        except Exception as e:
            print(f"Command failed: {e}")
            raise

    def log_serial(self, direction: str, message: str, max_width: int = 80):
        """Log serial communication with alignment"""
        if direction == "send":
            arrow = "→"
            print(f'{"[SIMULATION] " if self.simulate else ""}TX {arrow} {message}')
        else:  # receive
            arrow = "←"
            print(f'{"[SIMULATION] " if self.simulate else ""}RX {arrow} {message}')

    def initialize(self) -> None:
        """Initialize the plate reader"""
        if self.simulate:
            print("[SIMULATION] Plate Reader initialized")
            return
        # TODO get serial number
        info_command = CDCLCommand(
            command=GenericInstructionPrefixes.GET_INFO)
        info_response = self.send_command(info_command, timeout=60)
        print(info_response)
        # find the param that starts with "n" and slice the prefix
        self.name = next(
            x for x in info_response.params if x.startswith("n"))[1:]
        # find the param that starts with "n" and slice the prefix
        self.model_number = next(
            x for x in info_response.params if x.startswith("m"))[1:]
        self.firmware_version = next(
            x for x in info_response.params if x.startswith("f"))[1:]

        status_command = CDCLCommand(
            command=GenericInstructionPrefixes.GET_STATUS)
        status_response = self.send_command(status_command)
        self.status = status_response.params[0]

        wavelength_command = CDCLCommand(
            command=PlateReaderSpecificInstructionPrefixes.GET_WAVELENGTHS)
        wavelength_response = self.send_command(wavelength_command)
        if wavelength_response.params:
            self.wavelengths = list(map(int, wavelength_response.params))

        print(self)

    def calibrate(self, wavelength: int):
        wavelength_index = self.wavelengths.index(wavelength)
        if wavelength_index == -1:
            raise ValueError(f'wavelength {wavelength} not found on device')
        mode = PlateReaderModeCalculator.set_led_mode(0, wavelength_index)
        calibrate_command = CDCLCommand(
            command=PlateReaderSpecificInstructionPrefixes.CALIBRATE, params=[str(mode)])
        return self.send_command(calibrate_command)

    def read_absorbance(self, wavelength: int, interval: int, duration: int,  **kwargs) -> Dict[str, Any]:
        """Read absorbance at specified wavelength"""
        if self.simulate:
            print("[SIMULATION] Read absorbance")
        wavelength_index = self.wavelengths.index(wavelength)
        if wavelength_index == -1:
            raise ValueError(f'wavelength {wavelength} not found on device')
        mode = PlateReaderModeCalculator.set_led_mode(0, wavelength_index)
        experiment_setup_command = CDCLCommand(
            command=PlateReaderSpecificInstructionPrefixes.EXPERIMENT_SETUP)
        self.send_command(experiment_setup_command)
        mode_setup_command = CDCLCommand(
            command=PlateReaderSpecificInstructionPrefixes.EXPERIMENT_SETUP, params=[f'{StartCommandPrefixes.MODE} {mode}'])
        end_setup_command = CDCLCommand(
            command=PlateReaderSpecificInstructionPrefixes.EXPERIMENT_SETUP, params=StartCommandPrefixes.EXECUTE)
        self.send_command(mode_setup_command)
        self.send_command(end_setup_command)

        data_response = None
        while (data_response == None):
            line = self._connection.readline().decode().strip()
            self.log_serial(direction="receive", message=line)
            if CDCLParser.is_cdcl_response(line):
                response = CDCLParser.parse_response(line)
                if (response.prefix == GenericResponsePrefixes.DATA_TRANSMISSION):
                    data_response = response
        return data_response

    def start_experiment(self, builder: FullExperimentBuilder) -> Dict[str, any]:
        messages = builder.build_all()
        for message in messages:
            self.send_command(message)
            data_response = None
        while (data_response == None):
            line = self._connection.readline().decode().strip()
            self.log_serial(direction="receive", message=line)
            if CDCLParser.is_cdcl_response(line):
                response = CDCLParser.parse_response(line)
                if (response.prefix == GenericResponsePrefixes.DATA_TRANSMISSION):
                    data_response = response
        return data_response
