# __init__.py : edge

__version__ = '1.0.0'

# Import sub packages
from . import ifeatures

# Import modules in sub-packages
from .devices.device import Device
from .features.platform_information import PlatformInformation
from .features.onboard_sensors import OnboardSensors
from .features.gpio import Gpio
from .features.memory import Memory
from .features.disk_info import DiskInfo

from .dmi_info import DmiInfo