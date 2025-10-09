from abc import abstractmethod
from typing import List
from typing import Union
from enum import Enum

from .ifeature import IFeature

class TemperatureSources(Enum):
    """
    Enum for temperature sources.
    """

    Cpu = 0
    """
    CPU temperature.
    """

    Cpu2 = 1
    """
    Second CPU temperature.
    """

    System = 2
    """
    System temperature.
    """

    Chipset = 3
    """
    Chipset temperature.
    """

    Gpu = 4
    """
    GPU temperature.
    """

class VoltageSources(Enum):
    """
    Enum for voltage sources.
    """
        
    Core = 0
    """
    Core voltage.
    """

    Core2 = 1
    """
    Second core voltage.
    """

    Battery = 2
    """
    Battery voltage.
    """

    Bus2P5V = 3
    """
    2.5V bus voltage.
    """

    Bus3P3V = 4
    """
    3.3V bus voltage.
    """

    Bus5V = 5
    """
    5V bus voltage.
    """

    Bus12V = 6
    """
    12V bus voltage.
    """

    Bus24V = 7
    """
    24V bus voltage.
    """

    BusMinus5V = 8
    """
    -5V bus voltage.
    """

    BusMinus12V = 9
    """
    -12V bus voltage.
    """

class FanSources(Enum):
    """
    Enum for fan sources.
    """

    Cpu = 0
    """
    CPU fan.
    """

    Cpu2 = 1
    """
    Second CPU fan.
    """
    
    System = 2
    """
    System fan.
    """
    
class CurrentSources(Enum):
    """
    Enum for current sources.
    """

class PowerSources(Enum):
    """
    Enum for power sources.
    """  

class IOnboardSensors(IFeature):
    """
    Interface for onboard sensors.
    This interface provides methods to retrieve temperature, voltage, and fan speed
    information from various sources on the motherboard.
    """
    
    @property
    @abstractmethod
    def temperature_sources(self) -> List[str]:
        """
        List of temperature sources.
        Returns:
            List[str]: List of temperature source names.
        """
        pass

    @abstractmethod
    def get_temperature(self, src: Union[str, TemperatureSources]) -> Union[float, None]:
        """
        Get the temperature for a given source.
        Args:
            src (str | TemperatureSources): The source name.
        Returns:
            float: The temperature value.
        """
        pass
    
    @property
    @abstractmethod
    def voltage_sources(self) -> List[str]:
        """
        List of voltage sources.
        Returns:
            List[str]: List of voltage source names.
        """
        pass

    @abstractmethod
    def get_voltage(self, src: Union[str, VoltageSources]) -> Union[float, None]:
        """
        Get the voltage for a given source.
        Args:
            src (str | VoltageSources): The source name.
        Returns:
            float: The voltage value.
        """
        pass

    @property
    @abstractmethod
    def fan_sources(self) -> List[str]:
        """
        List of fan sources.
        Returns:
            List[str]: List of fan source names.
        """
        pass
    
    @abstractmethod
    def get_fan_speed(self, src: Union[str, FanSources]) -> Union[float, None]:
        """
        Get the fan speed for a given source.
        Args:
            src (str | FanSources): The source name.
        Returns:
            float: The fan speed value.
        """
        pass