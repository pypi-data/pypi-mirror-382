from abc import abstractmethod
from typing import List
from typing import Union
from enum import Enum

from .ifeature import IFeature

class GpioDirectionTypes(Enum):
    """
    GPIO direction type
    """
    
    Input = 0
    """
    Input direction
    """
    
    Output = 1
    """
    Output direction
    """
    
class GpioLevelTypes(Enum):
    """
    GPIO level type
    """
    
    Low = 0
    """
    Low level
    """
    
    High = 1
    """
    High level
    """

class InputLevelChangedEventTypes(Enum):
    """
    GPIO input level changed event types
    """
    
    RisingEdge = 0
    """
    Rising edge event
    """
    
    FallingEdge = 1
    """
    Falling edge event
    """

class IGpio(IFeature):
    """
    GPIO feature interface
    """
    
    @property
    @abstractmethod
    def pin_names(self) -> List[str]:
        """
        List of GPIO pins
        Returns:
            List[str]: List of GPIO pins
        """
        pass
    
    @property
    @abstractmethod
    def max_pin_num(self) -> int:
        """
        Maximum GPIO pin index
        Returns:
            int: Maximum GPIO pin index
        """
        pass
    
    @abstractmethod
    def get_direction(self, pin: Union[str, int]) -> Union[GpioDirectionTypes, None]:
        """
        Get the direction of the GPIO
        Args:
            pin (str | int): GPIO name or index
        Returns:
            (GpioDirectionType | None): GPIO direction type
        """
        pass

    @abstractmethod
    def set_direction(self, pin: Union[str, int], direction: GpioDirectionTypes) -> None:
        """
        Set the direction of the GPIO
        Args:
            pin (str | int): GPIO name or index
            direction (GpioDirectionType): GPIO direction type
        """
        pass

    @abstractmethod
    def get_level(self, pin: Union[str, int]) -> Union[GpioLevelTypes, None]:
        """
        Get the level of the GPIO
        Args:
            pin (str | int): GPIO name or index
        Returns:
            (GpioLevelType | None): GPIO level type
        """
        pass

    @abstractmethod
    def set_level(self, pin: Union[str, int], level: GpioLevelTypes) -> None:
        """
        Set the level of the GPIO
        Args:
            pin (str | int): GPIO name or index
            level (GpioLevelType): GPIO level type
        """
        pass