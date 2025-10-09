import threading
from typing import List
from typing import Union

from .._internal._feature_provider._feature_provider import _FeatureProvider

from ..ifeatures.igpio import IGpio
from ..ifeatures.igpio import GpioDirectionTypes
from ..ifeatures.igpio import GpioLevelTypes

class Gpio(IGpio):
    
    ################################################################

    __instance = None 
    __lock = threading.Lock()
    
    def __new__(cls):
        with cls.__lock:
            if not cls.__instance:
                cls.__instance = super(Gpio, cls).__new__(cls)
            return cls.__instance
    
    def __init__(self):

        # Check if the class is already initialized
        if not hasattr(self, '_initialized'):

            # Initialize the flag
            self._initialized = True

            # Initialize feature provider instance
            self.__provider = _FeatureProvider()
    
    ################################################################
    
    @property
    def is_supported(self) -> bool:
        return self.__provider.is_gpio_supported
    
    ################################################################

    @property
    def pin_names(self) -> List[str]:
        return self.__provider.gpio_pins

    @property
    def max_pin_num(self) -> int:
        return self.__provider.gpio_max_pin_num

    def get_direction(self, pin: Union[str, int]) -> Union[GpioDirectionTypes, None]:
        return self.__provider.gpio_get_direction(pin)

    def set_direction(self, pin: Union[str, int], direction: GpioDirectionTypes) -> None:
        self.__provider.gpio_set_direction(pin, direction)

    def get_level(self, pin: Union[str, int]) -> Union[GpioLevelTypes, None]:
        return self.__provider.gpio_get_level(pin)

    def set_level(self, pin: Union[str, int], level: GpioLevelTypes) -> None:
        self.__provider.gpio_set_level(pin, level)