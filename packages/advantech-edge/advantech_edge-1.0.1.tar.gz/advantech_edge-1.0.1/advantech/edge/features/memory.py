import threading
from typing import Union

from .._internal._feature_provider._feature_provider import _FeatureProvider

from ..ifeatures.imemory import IMemory

class Memory(IMemory):
    
    ################################################################

    __instance = None
    __lock = threading.Lock()

    def __new__(cls):
        with cls.__lock:
            if not cls.__instance:
                cls.__instance = super(Memory, cls).__new__(cls)
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
        return self.__provider.is_memory_supported

    ################################################################

    @property
    def count(self) -> int:
        return self.__provider.memory_count

    def get_type(self, index: int) -> Union[str, None]:
        return self.__provider.memory_get_type(index)

    def get_module_type(self, index: int) -> Union[str, None]:
        return self.__provider.memory_get_module_type(index)

    def get_size_in_GB(self, index: int) -> Union[int, None]:
        return self.__provider.memory_get_size_in_GB(index)

    def get_speed(self, index: int) -> Union[str, None]:
        return self.__provider.memory_get_speed(index)

    def get_rank(self, index: int) -> Union[int, None]:
        return self.__provider.memory_get_rank(index)

    def get_voltage(self, index: int) -> Union[float, None]:
        return self.__provider.memory_get_voltage(index)

    def get_bank(self, index: int) -> Union[str, None]:
        return self.__provider.memory_get_bank(index)

    def get_manufacturing_date_code(self, index: int) -> Union[str, None]:
        return self.__provider.memory_get_manufacturing_date_code(index)

    def get_temperature(self, index: int) -> Union[float, None]:
        return self.__provider.memory_get_temperature(index)

    def get_write_protection(self, index: int) -> Union[str, None]:
        return self.__provider.memory_get_write_protection(index)

    def get_module_manufacturer(self, index: int) -> Union[str, None]:
        return self.__provider.memory_get_module_manufacture(index)

    def get_manufacturer(self, index: int) -> Union[str, None]:
        return self.__provider.memory_get_manufacture(index)

    def get_part_number(self, index: int) -> Union[str, None]:
        return self.__provider.memory_get_part_number(index)

    def get_specific(self, index: int) -> Union[str, None]:
        return self.__provider.memory_get_specific(index)