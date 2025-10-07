from typing import Dict, Any, List, Optional
from .base_plate_reader import CerilloBasePlateReader


class StratusReader(CerilloBasePlateReader):
    """Stratus plate reader implementation"""

    def __init__(self, port: str = '/dev/ttyUSB0', **kwargs):
        super().__init__(port, baudrate=250000, **kwargs)
        self.plate_type = "96-well"
