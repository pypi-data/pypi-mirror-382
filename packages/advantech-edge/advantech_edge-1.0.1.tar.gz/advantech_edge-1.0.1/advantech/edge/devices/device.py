
import threading

from ..idevices.idevice import IDevice

from ..features.platform_information import PlatformInformation
from ..features.onboard_sensors import OnboardSensors
from ..features.gpio import Gpio
from ..features.watchdog import Watchdog
from ..features.memory import Memory
from ..features.disk_info import DiskInfo

class Device(IDevice):
    """
    Device class that provides access to various device features.
    """

    ################################################################
    
    __instance = None
    __lock = threading.Lock()
    
    def __new__(cls):
        with cls.__lock:
            if not cls.__instance:
                cls.__instance = super(Device, cls).__new__(cls)
            return cls.__instance

    def __init__(self):

        # Check if the class is already initialized
        if not hasattr(self, '_initialized'):

            # Initialize the flag
            self._initialized = True

            # Initialize feature instances
            self.__platform_information = PlatformInformation()
            self.__onboard_sensors = OnboardSensors()
            self.__gpio = Gpio()
            self.__watchdog = Watchdog()
            self.__memory = Memory()
            self.__disk = DiskInfo()

    ################################################################

    @property
    def description(self) -> str:
        return self.__platform_information.motherboard_name
    
    ################################################################
    
    @property
    def platform_information(self) -> PlatformInformation:
        """
        Get the platform information feature.
        Returns:
            PlatformInformation: The platform information feature instance.
        """
        return self.__platform_information
    
    @property
    def onboard_sensors(self) -> OnboardSensors:
        """
        Get the onboard sensors feature.
        Returns:
            OnboardSensors: The onboard sensors feature instance.
        """
        return self.__onboard_sensors
    
    @property
    def gpio(self) -> Gpio:
        """
        Get the GPIO feature.
        Returns:
            Gpio: The GPIO feature instance.
        """
        return self.__gpio
    
    @property
    def watchdog(self) -> Watchdog:
        """
        Get the Watchdog feature.
        Returns:
            Watchdog: The Watchdog feature instance.
        """
        return self.__watchdog
    
    @property
    def memory(self) -> Memory:
        """
        Get the memory feature.
        Returns:
            Memory: The memory feature instance.
        """
        return self.__memory
    
    @property
    def disk_info(self) -> DiskInfo:
        """
        Get the disk information feature.
        Returns:
            DiskInfo: The disk information feature instance.
        """
        return self.__disk