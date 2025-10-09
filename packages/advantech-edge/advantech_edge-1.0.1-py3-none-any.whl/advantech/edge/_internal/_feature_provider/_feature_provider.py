import os
import sys
import threading
from typing import List
from typing import Union

from ._platform_info_data import _PlatformInfoData

from .._susi_iot._susi_iot import _SusiIot
from .._eapi._eapi import _EApi

from ...ifeatures.ionboardsensors import TemperatureSources
from ...ifeatures.ionboardsensors import VoltageSources
from ...ifeatures.ionboardsensors import FanSources

from ...ifeatures.igpio import GpioDirectionTypes
from ...ifeatures.igpio import GpioLevelTypes

from ...dmi_info import DmiInfo

class _FeatureProvider:

    ################################################################

    @classmethod
    def is_root(cls):
        if os.geteuid() != 0:
            sys.exit("Error: Please run this program as root (use sudo).")
        else:
            return True

    ################################################################
    
    __instance = None 
    __lock = threading.Lock()
    
    def __new__(cls):

        # Check root authorization
        cls.is_root()

        # Create instance
        with cls.__lock:
            if not cls.__instance:
                cls.__instance = super(_FeatureProvider, cls).__new__(cls)
            return cls.__instance

    def __init__(self):
        
        # Check if the class is already initialized
        if not hasattr(self, '_initialized'):         

            # Initialize the flag
            self._initialized = True
            
            # Create lib instance
            if _SusiIot.is_lib_exists():
                self.__susi_iot : Union[_SusiIot, None] = _SusiIot()
                self.__eapi : Union[_EApi, None] = None
            elif _EApi.is_lib_exists():
                self.__susi_iot : Union[_SusiIot, None] = None
                self.__eapi : Union[_EApi, None] = _EApi()
            else:
                raise RuntimeError(f"Hardware library not installed.")
            
    def __del__(self):
        
        if self.__susi_iot is not None:
            del self.__susi_iot
        if self.__eapi is not None:
            del self.__eapi

    ################################################################

    # Feature : Platform Information
    
    @property
    def is_platform_information_supported(self) -> bool:
        
        if self.__susi_iot != None:
            return self.__susi_iot.is_platform_information_supported
        elif self.__eapi != None:
            return self.__eapi.is_platform_information_supported
        else:
            raise RuntimeError("Feature not supported : Platform Information.")

    @property
    def platform_info_data(self) -> _PlatformInfoData:
        
        if self.__susi_iot != None:
            return self.__susi_iot.platform_info_data
        elif self.__eapi != None:
            return self.__eapi.platform_info_data
        else:
            raise RuntimeError("Feature not supported : Platform Information.")
    
    ################################################################

    # Feature : Onboard Sensors
    
    @property
    def is_onboard_sensors_supported(self) -> bool:
        
        if self.__susi_iot != None:
            return self.__susi_iot.is_onboard_sensors_supported
        elif self.__eapi != None:
            return self.__eapi.is_onboard_sensors_supported
        else:
            raise RuntimeError("Feature not supported : Onboard Sensors.")
    
    @property
    def onboard_sensors_temperature_sources(self) -> List[str]:
        
        if self.__susi_iot != None:
            return self.__susi_iot.onboard_sensors_temperature_sources
        elif self.__eapi != None:
            return self.__eapi.onboard_sensors_temperature_sources
        else:
            raise RuntimeError("Feature not supported : Onboard Sensors.")

    def onboard_sensors_get_temperature(self, src: Union[str, TemperatureSources]) -> Union[float, None]:

        if self.__susi_iot != None:
            return self.__susi_iot.onboard_sensors_get_temperature(src)
        elif self.__eapi != None:
            return self.__eapi.onboard_sensors_get_temperature(src)
        else:
            raise RuntimeError("Feature not supported : Onboard Sensors.")

    @property
    def onboard_sensors_voltage_sources(self) -> List[str]:
        
        if self.__susi_iot != None:
            return self.__susi_iot.onboard_sensors_voltage_sources
        elif self.__eapi != None:
            return self.__eapi.onboard_sensors_voltage_sources
        else:
            raise RuntimeError("Feature not supported : Onboard Sensors.")

    def onboard_sensors_get_voltage(self, src: Union[str, VoltageSources]) -> Union[float, None]:
        
        if self.__susi_iot != None:
            return self.__susi_iot.onboard_sensors_get_voltage(src)
        elif self.__eapi != None:
            return self.__eapi.onboard_sensors_get_voltage(src)
        else:
            raise RuntimeError("Feature not supported : Onboard Sensors.")

    @property
    def onboard_sensors_fan_sources(self) -> List[str]:
        
        if self.__susi_iot != None:
            return self.__susi_iot.onboard_sensors_fan_sources
        elif self.__eapi != None:
            return self.__eapi.onboard_sensors_fan_sources
        else:
            raise RuntimeError("Feature not supported : Onboard Sensors.")
    
    def onboard_sensors_get_fan_speed(self, src: Union[str, FanSources]) -> Union[float, None]:
    
        if self.__susi_iot != None:
            return self.__susi_iot.onboard_sensors_get_fan_speed(src)
        elif self.__eapi != None:
            return self.__eapi.onboard_sensors_get_fan_speed(src)
        else:
            raise RuntimeError("Feature not supported : Onboard Sensors.")
    
    ################################################################

    # Feature : GPIO
    
    @property
    def is_gpio_supported(self) -> bool:
        
        if self.__susi_iot != None:
            return self.__susi_iot.is_gpio_supported
        elif self.__eapi != None:
            return self.__eapi.is_gpio_supported
        else:
            raise RuntimeError("Feature not supported : GPIO.")

    @property
    def gpio_pins(self) -> List[str]:
        
        if self.__susi_iot != None:
            return self.__susi_iot.gpio_pins
        elif self.__eapi != None:
            return self.__eapi.gpio_pins
        else:
            raise RuntimeError("Feature not supported : GPIO.")

    @property
    def gpio_max_pin_num(self) -> int:
        
        if self.__susi_iot != None:
            return self.__susi_iot.gpio_max_pin_num
        elif self.__eapi != None:
            return self.__eapi.gpio_max_pin_num
        else:
            raise RuntimeError("Feature not supported : GPIO.")

    def gpio_get_direction(self, pin: Union[str, int]) -> Union[GpioDirectionTypes, None]:
        
        if self.__susi_iot != None:
            return self.__susi_iot.gpio_get_direction(pin)
        elif self.__eapi != None:
            return self.__eapi.gpio_get_direction(pin)
        else:
            raise RuntimeError("Feature not supported : GPIO.")

    def gpio_set_direction(self, pin: Union[str, int], dir: GpioDirectionTypes) -> None:
        
        if self.__susi_iot != None:
            self.__susi_iot.gpio_set_direction(pin, dir)
        elif self.__eapi != None:
            self.__eapi.gpio_set_direction(pin, dir)
        else:
            raise RuntimeError("Feature not supported : GPIO.")

    def gpio_get_level(self, pin: Union[str, int]) -> Union[GpioLevelTypes, None]:
        
        if self.__susi_iot != None:
            return self.__susi_iot.gpio_get_level(pin)
        elif self.__eapi != None:
            return self.__eapi.gpio_get_level(pin)
        else:
            raise RuntimeError("Feature not supported : GPIO.")

    def gpio_set_level(self, pin: Union[str, int], level: GpioLevelTypes) -> None:
        
        if self.__susi_iot != None:
            self.__susi_iot.gpio_set_level(pin, level)
        elif self.__eapi != None:
            self.__eapi.gpio_set_level(pin, level)
        else:
            raise RuntimeError("Feature not supported : GPIO.")

    ################################################################

    # Feature : Watchdog
    
    @property
    def is_watchdog_supported(self) -> bool:
    
        if self.__susi_iot != None:
            return self.__susi_iot.is_watchdog_supported
        elif self.__eapi != None:
            return self.__eapi.is_watchdog_supported
        else:
            raise RuntimeError("Feature not supported : Watchdog.")
    
    @property
    def watchdog_timers(self) -> List[str]:
        
        if self.__susi_iot != None:
            return self.__susi_iot.watchdog_timers
        elif self.__eapi != None:
            return self.__eapi.watchdog_timers
        else:
            raise RuntimeError("Feature not supported : Watchdog.")

    def watchdog_start_timer(self, timer: Union[str, int], delay: int, event_timeout: int, reset_timeout: int) -> None:
        
        if self.__susi_iot != None:
            self.__susi_iot.watchdog_start_timer(timer, delay, event_timeout, reset_timeout)
        elif self.__eapi != None:
            self.__eapi.watchdog_start_timer(timer, delay, event_timeout, reset_timeout)
        else:
            raise RuntimeError("Feature not supported : Watchdog.")
    
    def watchdog_stop_timer(self, timer: Union[str, int]) -> None:
        
        if self.__susi_iot != None:
            self.__susi_iot.watchdog_stop_timer(timer)
        elif self.__eapi != None:
            self.__eapi.watchdog_stop_timer(timer)
        else:
            raise RuntimeError("Feature not supported : Watchdog.")
    
    def watchdog_trigger_timer(self, timer: Union[str, int]) -> None:
        
        if self.__susi_iot != None:
            self.__susi_iot.watchdog_trigger_timer(timer)
        elif self.__eapi != None:
            self.__eapi.watchdog_trigger_timer(timer)
        else:
            raise RuntimeError("Feature not supported : Watchdog.")

    ################################################################

    # Feature : Memory
    
    @property
    def is_memory_supported(self) -> bool:
        
        if self.__susi_iot != None:
            return self.__susi_iot.is_memory_supported
        elif self.__eapi != None:
            return False
        else:
            raise RuntimeError("Feature not supported : Memory.")

    @property
    def memory_count(self) -> int:
        
        if self.__susi_iot != None:
            return self.__susi_iot.memory_count
        elif self.__eapi != None:
            return 0
        else:
            raise RuntimeError("Feature not supported : Memory.")

    def memory_get_type(self, index: int) -> Union[str, None]:
        
        if self.__susi_iot != None:
            return self.__susi_iot.memory_get_type(index)
        elif self.__eapi != None:
            return None
        else:
            raise RuntimeError("Feature not supported : Memory.")

    def memory_get_module_type(self, index: int) -> Union[str, None]:
    
        if self.__susi_iot != None:
            return self.__susi_iot.memory_get_module_type(index)
        elif self.__eapi != None:
            return None
        else:
            raise RuntimeError("Feature not supported : Memory.")

    def memory_get_size_in_GB(self, index: int) -> Union[int, None]:
        
        if self.__susi_iot != None:
            return self.__susi_iot.memory_get_size_in_GB(index)
        elif self.__eapi != None:
            return None
        else:
            raise RuntimeError("Feature not supported : Memory.")

    def memory_get_speed(self, index: int) -> Union[str, None]:
        
        if self.__susi_iot != None:
            return self.__susi_iot.memory_get_speed(index)
        elif self.__eapi != None:
            return None
        else:
            raise RuntimeError("Feature not supported : Memory.")

    def memory_get_rank(self, index: int) -> Union[int, None]:
        
        if self.__susi_iot != None:
            return self.__susi_iot.memory_get_rank(index)
        elif self.__eapi != None:
            return None
        else:
            raise RuntimeError("Feature not supported : Memory.")

    def memory_get_voltage(self, index: int) -> Union[float, None]:
        
        if self.__susi_iot != None:
            return self.__susi_iot.memory_get_voltage(index)
        elif self.__eapi != None:
            return None
        else:
            raise RuntimeError("Feature not supported : Memory.")

    def memory_get_bank(self, index: int) -> Union[str, None]:
        
        if self.__susi_iot != None:
            return self.__susi_iot.memory_get_bank(index)
        elif self.__eapi != None:
            return None
        else:
            raise RuntimeError("Feature not supported : Memory.")

    def memory_get_manufacturing_date_code(self, index: int) -> Union[str, None]:
        
        if self.__susi_iot != None:
            return self.__susi_iot.memory_get_manufacturing_date_code(index)
        elif self.__eapi != None:
            return None
        else:
            raise RuntimeError("Feature not supported : Memory.")

    def memory_get_temperature(self, index: int) -> Union[float, None]:
        
        if self.__susi_iot != None:
            return self.__susi_iot.memory_get_temperature(index)
        elif self.__eapi != None:
            return None
        else:
            raise RuntimeError("Feature not supported : Memory.")

    def memory_get_write_protection(self, index: int) -> Union[str, None]:
    
        if self.__susi_iot != None:
            return self.__susi_iot.memory_get_write_protection(index)
        elif self.__eapi != None:
            return None
        else:
            raise RuntimeError("Feature not supported : Memory.")

    def memory_get_module_manufacture(self, index: int) -> Union[str, None]:
    
        if self.__susi_iot != None:
            return self.__susi_iot.memory_get_module_manufacture(index)
        elif self.__eapi != None:
            return None
        else:
            raise RuntimeError("Feature not supported : Memory.")

    def memory_get_manufacture(self, index: int) -> Union[str, None]:
        
        if self.__susi_iot != None:
            return self.__susi_iot.memory_get_manufacture(index)
        elif self.__eapi != None:
            return None
        else:
            raise RuntimeError("Feature not supported : Memory.")

    def memory_get_part_number(self, index: int) -> Union[str, None]:
        
        if self.__susi_iot != None:
            return self.__susi_iot.memory_get_part_number(index)
        elif self.__eapi != None:
            return None
        else:
            raise RuntimeError("Feature not supported : Memory.")
    
    def memory_get_specific(self, index: int) -> Union[str, None]:
        
        if self.__susi_iot != None:
            return self.__susi_iot.memory_get_specific(index)
        elif self.__eapi != None:
            return None
        else:
            raise RuntimeError("Feature not supported : Memory.")
    
    ################################################################

    # Feature : Disk Information
    
    @property
    def is_disk_info_supported(self) -> bool:
        
        if self.__susi_iot != None:
            return self.__susi_iot.is_disk_info_supported
        elif self.__eapi != None:
            return self.__eapi.is_disk_info_supported
        else:
            raise RuntimeError("Feature not supported : Disk Information.")
    
    @property
    def disk_info_disks(self) -> List[str]:
        
        if self.__susi_iot != None:
            return self.__susi_iot.disk_info_disks
        elif self.__eapi != None:
            return self.__eapi.disk_info_disks
        else:
            raise RuntimeError("Feature not supported : Disk Information.")
    
    def disk_info_get_total_space(self, disk: Union[str, int]) -> Union[int, None]:
        
        if self.__susi_iot != None:
            return self.__susi_iot.disk_info_get_total_space(disk)
        elif self.__eapi != None:
            return self.__eapi.disk_info_get_total_space(disk)
        else:
            raise RuntimeError("Feature not supported : Disk Information.")
    
    def disk_info_get_free_space(self, disk: Union[str, int]) -> Union[int, None]:
        
        if self.__susi_iot != None:
            return self.__susi_iot.disk_info_get_free_space(disk)
        elif self.__eapi != None:
            return self.__eapi.disk_info_get_free_space(disk)
        else:
            raise RuntimeError("Feature not supported : Disk Information.")