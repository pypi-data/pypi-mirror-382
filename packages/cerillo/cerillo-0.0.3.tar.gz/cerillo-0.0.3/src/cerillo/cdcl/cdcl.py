from dataclasses import dataclass
from typing import Optional, List, Any
import re


@dataclass
class CDCLResponse:
    """Parsed CDCL protocol response"""
    serial_number: int
    command_id: Optional[str]
    prefix: str
    params: List[str]
    raw_message: str

    def __repr__(self):
        cmd_str = f" cmd_id={self.command_id}" if self.command_id else ""
        return (f"CDCLResponse(serial={self.serial_number}{cmd_str}, "
                f"prefix='{self.prefix}', params={self.params})")

    def __post_init__(self):
        """Generate raw_message if not provided"""
        if not self.raw_message:
            self.raw_message = self.to_message()


@dataclass
class CDCLCommand:
    """parsed CDCL protocol command"""
    command: str
    command_id: Optional[str] = None
    params: Optional[List[str]] = None
    raw_message: str = ""

    def __repr__(self):
        cmd_str = f" command_id={self.command_id}" if self.command_id else ""
        return (f"CDCLCommand({cmd_str}, "
                f"command='{self.command}', params={self.params})")

    def __post_init__(self):
        """Generate raw_message if not provided"""
        if not self.raw_message:
            self.raw_message = self.to_message()

    def to_message(self) -> str:
        """Construct the raw CDCL message from components"""
        # Start with serial number
        # Add prefix
        msg = f"{self.command}"

        # Add command ID if present
        if self.command_id:
            msg += f"*{self.command_id}"

        # Add params if present
        if self.params:
            msg += " " + " ".join(str(p) for p in self.params)

        return msg


class CDCLParseError(Exception):
    """Exception raised when parsing CDCL message fails"""
    pass


class CDCLParser:
    """Parser for CDCL protocol messages"""

    # Regex pattern for CDCL response message
    # Format: :<serial>*[<cmd_id>*]<prefix> [params...]
    CDCL_RESPONSE_PATTERN = re.compile(
        r'^:'                                 # Colon at start
        # Serial number (group 1)
        r'([A-Za-z0-9]+)'
        # Optional 4-char base64 cmd ID (group 2)
        r'(?:\*([A-Za-z0-9\+\/]{4}))?\s'
        # Single char prefix (group 3)
        r'([A-Za-z0-9])'
        # Optional space and params (group 4)
        r'\s*(?:(.*))?$'
    )

    CDCL_COMMAND_PATTERN = re.compile(
        r'^'
        r'([\S]{1})'
        r'(?:\*([A-Za-z0-9\+\/]{4}))?'
        r'\s*(?:(.*))?$'
    )

    @classmethod
    def parse_response(cls, message: str) -> CDCLResponse:
        """
        Parse a CDCL protocol message.

        Args:
            message: Raw CDCL message string

        Returns:
            CDCLResponse object with parsed fields

        Raises:
            CDCLParseError: If message doesn't match CDCL format
        """
        if not message:
            raise CDCLParseError("Empty message")

        # Strip whitespace
        message = message.strip()

        # Check for colon prefix
        if not message.startswith(':'):
            raise CDCLParseError(
                f"Response message must start with ':' (got: {message[:10]}...)"
            )

        # Match the pattern
        match = cls.CDCL_RESPONSE_PATTERN.match(message)
        if not match:
            raise CDCLParseError(
                f"Response message doesn't match CDCL format: {message}"
            )

        # Extract components
        serial_number, cmd_id, prefix, params_str = match.groups()

        # Parse parameters (whitespace-separated)
        params = params_str.split() if params_str else []

        return CDCLResponse(
            serial_number=serial_number,
            command_id=cmd_id,
            prefix=prefix,
            params=params,
            raw_message=message
        )

    @classmethod
    def parse_command(cls, command: str) -> CDCLCommand:
        """
        Parse a CDCL protocol command

        Args:
            command: Raw CDCL command string

        Returns:
            CDCLCommand object with parsed fields

        Raises:
            CDCLParseError: If command doesn't match CDCL format"""
        if not command:
            raise CDCLParseError("Empty message")

        # Strip whitespace
        message = command.strip()

        match = cls.CDCL_COMMAND_PATTERN.match(command)
        if not match:
            raise CDCLParseError(
                f"Command doesn't match CDCL format: {command}"
            )

        command_prefix, command_id, params_str = match.groups()

        # Parse parameters (whitespace-separated)
        params = params_str.split() if params_str else []

        return CDCLCommand(
            command=command_prefix,
            command_id=command_id,
            params=params,
            raw_message=message
        )

    @classmethod
    def is_cdcl_response(cls, message: str) -> bool:
        """
        Check if a message looks like a CDCL message without full parsing.

        Args:
            message: String to check

        Returns:
            True if message starts with colon and looks like CDCL format
        """
        if not message or not isinstance(message, str):
            return False
        return message.strip().startswith(':')

    @classmethod
    def parse_param_as_int(cls, param: str) -> int:
        """Parse a parameter as integer with error handling"""
        try:
            return int(param)
        except (ValueError, TypeError):
            raise CDCLParseError(f"Cannot parse '{param}' as integer")

    @classmethod
    def parse_param_as_float(cls, param: str) -> float:
        """Parse a parameter as float with error handling"""
        try:
            return float(param)
        except (ValueError, TypeError):
            raise CDCLParseError(f"Cannot parse '{param}' as float")


class PlateReaderModeCalculator:
    """Utility class for manipulating plate reader mode bits"""

    @staticmethod
    def set_led_mode(base_mode: int, led_index: int) -> int:
        """
        Set the LED mode in a mode value.

        Args:
            base_mode: The base mode value to modify
            led_index: The LED index to set (0-7)

        Returns:
            Modified mode value with LED index set
        """
        # Un-set the LED mode field (bits 25-30, 6 bits total)
        base_mode &= ~(0b111111 << 25)

        # Add the new LED index value
        led_val_to_add = (2 ** 25) * led_index
        return base_mode + led_val_to_add

    @staticmethod
    def get_led_index(mode: int) -> int:
        """
        Extract the LED index from a mode value.

        Args:
            mode: Mode value to dissect

        Returns:
            LED index (0-7)
        """
        led_mode = (mode >> 25) - (mode >> 28)
        return led_mode
