import json
import threading

from typing import List
from typing import Dict
from typing import Union

from ._susi_iot_ids import _SusiIotId, _SusiIotIdUtilities
from ._susi_iot_functions import _SusiIotFunctions
from ._susi_iot_gpio import _SusiIotGpioDirectionType, _SusiIotGpioLevelType

from .._feature_provider._platform_info_data import _PlatformInfoData

from ...ifeatures.ionboardsensors import TemperatureSources
from ...ifeatures.ionboardsensors import VoltageSources
from ...ifeatures.ionboardsensors import FanSources

from ...ifeatures.igpio import GpioDirectionTypes, GpioLevelTypes

from ...dmi_info import DmiInfo

class _SusiIot:

    ################################################################

    __instance = None
    __lock = threading.Lock()
    
    def __new__(cls):

        # Check library existence
        if _SusiIotFunctions.is_lib_exists() == False:
            raise ModuleNotFoundError("SUSI IoT")

        # Create instance
        with cls.__lock:
            if not cls.__instance:
                cls.__instance = super(_SusiIot, cls).__new__(cls)
            return cls.__instance
    
    def __init__(self):

        # Check if the class is already initialized
        if not hasattr(self, '_initialized'):

            # Initialize the flag
            self._initialized = True
        
            # Create SUSI IoT instance
            self.__funcs = _SusiIotFunctions()

            #
            self.__cap_init()
            self.__id_list = self.__extract_ids(self.__cap)
            
            # 
            self.__dict_onboard_sensors_temperature_ids = self.__read_temperature_dict()
            self.__dict_onboard_sensors_voltage_ids = self.__read_voltage_dict()
            self.__dict_onboard_sensors_fan_ids = self.__read_fan_dict()
            self.__dict_gpio_pin_ids = self.__read_gpio_pin_id_dict()
            self.__dict_memory = self.__read_memory_dict()
            self.__dict_disks = self.__read_disk_dict()
    
    def __del__(self):
        
        if self.__funcs is not None:
            del self.__funcs

    ################################################################

    def __cap_init(self) -> None:

        # Get capability string
        cap_string = self.__funcs.get_capability_string()

        # Decode JSON string to JSON object
        cap = None
        try:
            cap = json.loads(cap_string)
        except json.JSONDecodeError as e:
            raise e
            
        # Store capability JSON object as private field
        self.__cap = cap

    def __extract_ids(self, obj, result = None) -> list:

        if result is None:
            result = []

        if isinstance(obj, dict):
            
            if "id" in obj:
                
                try:
                    id = _SusiIotId(obj["id"])
                    result.append(id)
                except ValueError:
                    pass
                
            for value in obj.values():
                self.__extract_ids(value, result)
                
        elif isinstance(obj, list):
            
            for item in obj:
                self.__extract_ids(item, result)

        return result

    ################################################################

    def __read_temperature_dict(self) -> Dict[str, _SusiIotId]:

        tbl = {}

        # onboard temperatures
        first_id = _SusiIotId.HardwareMonitorTemperatureCpu
        for i in range(20):
            
            try:
                id = _SusiIotId(first_id.value + i)
                if id not in self.__id_list:
                    continue
            except ValueError:
                continue
            
            data_json_obj = self.__funcs.get_data_by_id(id)
            if data_json_obj == None:
                continue
            if 'n' not in data_json_obj:
                continue
            
            name = data_json_obj['n']
            tbl.update({name: id})

        # memory temperatures
        first_id = _SusiIotId.SdramMemoryTemperature0
        for i in range(20):
            
            try:
                id = _SusiIotId(first_id.value + i)
                if id not in self.__id_list:
                    continue
            except ValueError:
                continue
            
            data_json_obj = self.__funcs.get_data_by_id(id)
            if data_json_obj == None:
                continue
            if 'n' not in data_json_obj:
                continue
            
            name = data_json_obj['n']
            tbl.update({name: id})
        
        return tbl

    def __read_voltage_dict(self) -> Dict[str, _SusiIotId]:

        tbl = {}
        
        # onboard voltages
        first_id = _SusiIotId.HardwareMonitorVoltageCore
        for i in range(64):
            
            try:
                id = _SusiIotId(first_id.value + i)
                if id not in self.__id_list:
                    continue
            except ValueError:
                continue
            
            data_json_obj = self.__funcs.get_data_by_id(id)
            if data_json_obj == None:
                continue
            if 'n' not in data_json_obj:
                continue

            name = data_json_obj['n']
            tbl.update({name: id})
        
        return tbl

    def __read_fan_dict(self) -> Dict[str, _SusiIotId]:
        
        tbl = {}
        
        # onboard fan speeds
        first_id = _SusiIotId.HardwareMonitorFanSpeedCpu
        for i in range(64):
            
            try:
                id = _SusiIotId(first_id.value + i)
                if id not in self.__id_list:
                    continue
            except ValueError:
                continue
            
            data_json_obj = self.__funcs.get_data_by_id(id)
            if data_json_obj == None:
                continue
            if 'n' not in data_json_obj:
                continue
                
            name = data_json_obj['n']
            tbl.update({name: id})
        
        return tbl

    def __read_gpio_pin_id_dict(self) -> Dict[str, _SusiIotId]:

        dict_gpio_pin_ids = {}
        
        # onbaord gpio
        first_id = _SusiIotId.Gpio00
        for i in range(64):
            
            # Try to convert ID value to ID enum
            try:
                pin_id = _SusiIotId(first_id.value + i)
                if pin_id not in self.__id_list:
                    continue
            except ValueError:
                continue
            
            # Try to get GPIO ID tuple via pin ID
            try:
                gpio_id_tuple = _SusiIotIdUtilities.gpio_pin_id_to_gpio_id_tuple(pin_id)
            except Exception as e:
                continue
            
            # Try to get data via pin ID
            data_json_obj = self.__funcs.get_data_by_id(pin_id)
            if data_json_obj == None:
                continue
            if 'bn' not in data_json_obj:
                continue
            name = data_json_obj['bn']
            
            # Update dictionary
            dict_gpio_pin_ids.update({name: pin_id})
                
        return dict_gpio_pin_ids

    def __read_memory_dict(self) -> Dict[str, _SusiIotId]:

        tbl = {}
        
        # SDRAMs
        first_id = _SusiIotId.Sdram0
        for i in range(64):
            
            try:
                id = _SusiIotId(first_id.value + i)
                if id not in self.__id_list:
                    continue
            except ValueError:
                continue
            
            data_json_obj = self.__funcs.get_data_by_id(id)
            if data_json_obj == None:
                continue
            if 'bn' not in data_json_obj:
                continue
                
            name = data_json_obj['bn']
            tbl.update({name: id})
        
        return tbl

    def __read_disk_dict(self) -> Dict[str, _SusiIotId]:
        
        tbl = { }
        
        # Disks
        first_id = _SusiIotId.DiskInfoTotalDiskSpace
        for i in range(1):
            
            try:
                id = _SusiIotId(first_id.value + i)
                if id not in self.__id_list:
                    continue
            except ValueError:
                continue
            
            data_json_obj = self.__funcs.get_data_by_id(id)
            if data_json_obj == None:
                continue
            if 'bn' not in data_json_obj:
                continue
                
            name = data_json_obj['bn']
            tbl.update({name: id})
        
        return tbl

    ################################################################
    
    # Check library existence
    
    @classmethod
    def is_lib_exists(cls) -> bool:
        return _SusiIotFunctions.is_lib_exists()

    ################################################################
    
    # Feature : Platform Information

    @property
    def is_platform_information_supported(self) -> bool:
        return True
    
    @property
    def platform_info_data(self) -> _PlatformInfoData:
        
        data_json_obj = self.__funcs.get_data_by_id(_SusiIotId.BoardName)
        motherboard_name = data_json_obj["sv"] if "sv" in data_json_obj else "Advantech Device"
        
        data_json_obj = self.__funcs.get_data_by_id(_SusiIotId.BoardManufacturer)
        manufacturer = data_json_obj["sv"] if "sv" in data_json_obj else "Advantech Co., Ltd."
        
        data_json_obj = self.__funcs.get_data_by_id(_SusiIotId.BootUpTimes)
        boot_up_times = data_json_obj["v"] if "v" in data_json_obj else None
        
        data_json_obj = self.__funcs.get_data_by_id(_SusiIotId.RunningTimeInHours)
        running_time_in_hours = data_json_obj["v"] if "v" in data_json_obj else None
        
        data_json_obj = self.__funcs.get_data_by_id(_SusiIotId.BiosRevision)
        bios_revision = data_json_obj["sv"] if "sv" in data_json_obj else None
        
        data_json_obj = self.__funcs.get_data_by_id(_SusiIotId.FirmwareName)
        firmware_name = data_json_obj["sv"] if "sv" in data_json_obj else None
        
        data_json_obj = self.__funcs.get_data_by_id(_SusiIotId.FirmwareVersion)
        firmware_version = data_json_obj["sv"] if "sv" in data_json_obj else None
        
        data_json_obj = self.__funcs.get_data_by_id(_SusiIotId.LibraryVersion)
        library_version = data_json_obj["sv"] if "sv" in data_json_obj else None
        
        data_json_obj = self.__funcs.get_data_by_id(_SusiIotId.DriverVersion)
        driver_version = data_json_obj["sv"] if "sv" in data_json_obj else None
        
        ec_revision = None  # to be implemented in the future
        
        dmi_info = None  # to be implemented in the future
    
        return _PlatformInfoData(
            motherboard_name = motherboard_name,
            manufacturer = manufacturer,
            boot_up_times = boot_up_times,
            running_time_in_hours = running_time_in_hours,
            bios_revision = bios_revision,
            firmware_name = firmware_name,
            firmware_version = firmware_version,
            library_version = library_version,
            driver_version = driver_version,
            ec_revision = ec_revision,
            dmi_info = dmi_info
        )

    ################################################################
    
    # Feature : Onboard Sensors
    
    @property
    def is_onboard_sensors_supported(self) -> bool:
        count = 0
        count += len(self.__dict_onboard_sensors_temperature_ids)
        count += len(self.__dict_onboard_sensors_voltage_ids)
        count += len(self.__dict_onboard_sensors_fan_ids)
        return count > 0
    
    @property
    def onboard_sensors_temperature_sources(self) -> List[str]:
        return list(self.__dict_onboard_sensors_temperature_ids.keys())

    def onboard_sensors_get_temperature(self, src : Union[str, TemperatureSources]) -> Union[float, None]:
        
        # Convert src to ID
        if isinstance(src, str):
            try:
                id = self.__dict_onboard_sensors_temperature_ids[src]
            except KeyError:
                return None
        elif isinstance(src, TemperatureSources):
            try:
                id = _SusiIotIdUtilities.temperature_sources_to_susi_iot_id(src)
            except Exception as e:
                return None
        else:
            return None
        
        # Check if specified ID is in list.
        found: bool = False
        for key, value in self.__dict_onboard_sensors_temperature_ids.items():
            if value == id:
                found = True
                break
        if not found:
            return None
        
        # Get data
        data_json_obj = self.__funcs.get_data_by_id(id)
        if 'v' not in data_json_obj:
            return None
        try:
            value = float(data_json_obj['v'])
        except (ValueError, TypeError):
            return None

        return value
    
    @property
    def onboard_sensors_voltage_sources(self) -> List[str]:
        return list(self.__dict_onboard_sensors_voltage_ids.keys())

    def onboard_sensors_get_voltage(self, src : Union[str, VoltageSources]) -> Union[float, None]:
        
        # Convert src to ID
        if isinstance(src, str):
            try:
                id = self.__dict_onboard_sensors_voltage_ids[src]
            except KeyError:
                return None
        elif isinstance(src, VoltageSources):
            try:
                id = _SusiIotIdUtilities.voltage_sources_to_susi_iot_id(src)
            except Exception as e:
                return None
        else:
            return None
        
        # Check if specified ID is in list.
        found: bool = False
        for key, value in self.__dict_onboard_sensors_voltage_ids.items():
            if value == id:
                found = True
                break
        if not found:
            return None
        
        # Get data
        data_json_obj = self.__funcs.get_data_by_id(id)
        if 'v' not in data_json_obj:
            return None       
        try:
            value = float(data_json_obj['v'])
        except (ValueError, TypeError):
            return None

        return value
    
    @property
    def onboard_sensors_fan_sources(self) -> List[str]:
        return list(self.__dict_onboard_sensors_fan_ids.keys())
    
    def onboard_sensors_get_fan_speed(self, src : Union[str, FanSources]) -> Union[float, None]:
        
        # Convert src to ID
        if isinstance(src, str):
            try:
                id = self.__dict_onboard_sensors_fan_ids[src]
            except KeyError:
                return None
        elif isinstance(src, FanSources):
            try:
                id = _SusiIotIdUtilities.fan_sources_to_susi_iot_id(src)
            except Exception as e:
                return None
        else:
            return None
        
        # Check if specified ID is in list.
        found: bool = False
        for key, value in self.__dict_onboard_sensors_fan_ids.items():
            if value == id:
                found = True
                break
        if not found:
            return None
        
        # Get data
        data_json_obj = self.__funcs.get_data_by_id(id)
        if 'v' not in data_json_obj:
            return None
        try:
            value = float(data_json_obj['v'])
        except (ValueError, TypeError):
            return None

        return value
    
    ################################################################
    
    # Feature : GPIO
    
    @property
    def is_gpio_supported(self) -> bool:
        return len(self.__dict_gpio_pin_ids) > 0

    @property
    def gpio_pins(self) -> List[str]:
        return list(self.__dict_gpio_pin_ids.keys())
    
    @property
    def gpio_max_pin_num(self) -> int:
        return len(self.__dict_gpio_pin_ids)

    def gpio_get_direction(self, pin: Union[str, int]) -> Union[GpioDirectionTypes, None]:
        
        # Check feature support
        if not self.is_gpio_supported:
            raise RuntimeError(f"Feature not supported : GPIO")
        
        # Get pin id from parameter
        if isinstance(pin, str):
            if pin not in self.__dict_gpio_pin_ids:
                return None
            pin_id = self.__dict_gpio_pin_ids[pin]
        elif isinstance(pin, int):
            try:
                pin_id = _SusiIotIdUtilities.gpio_pin_index_to_susi_iot_id_tuple(pin).pin_id
            except Exception as e:
                return None
        else:
            raise TypeError(f"Invalid pin type : {type(pin)}")
        
        # Check if pin ID is in dict.
        found: bool = False
        for key, value in self.__dict_gpio_pin_ids.items():
            if value == pin_id:
                found = True
                break
        if not found:
            return None
        
        # Calculate GPIO direction ID and check if it is in GPIO ID tuple dict.
        try:
            id_diff = pin_id.value - _SusiIotId.Gpio00.value
            pin_dir_id = _SusiIotId(_SusiIotId.GpioDir00.value + id_diff)
            if not _SusiIotIdUtilities.gpio_check_dir_id_in_susi_iot_id_tuple(pin_dir_id):
                return None
        except ValueError:
            return None
        
        # Get GPIO direction
        data_json_obj = self.__funcs.get_data_by_id(pin_dir_id)
        if 'bv' not in data_json_obj:
            return None
        try:
            dir = _SusiIotGpioDirectionType(data_json_obj['bv'])
        except ValueError:
            return None
        
        # Convert direction type
        converted_dir = _SusiIotIdUtilities.susi_iot_gpio_direction_type_to_gpio_direction_types(dir)
        
        # Return value
        return converted_dir

    def gpio_set_direction(self, pin: Union[str, int], dir: GpioDirectionTypes) -> None:
        
        # Check feature support
        if not self.is_gpio_supported:
            raise RuntimeError(f"Feature not supported : GPIO")
        
        # Get pin id from parameter
        if isinstance(pin, str):
            if pin not in self.__dict_gpio_pin_ids:
                raise RuntimeError(f"Invalid pin name : {pin}")
            pin_id = self.__dict_gpio_pin_ids[pin]
        elif isinstance(pin, int):
            try:
                pin_id = _SusiIotIdUtilities.gpio_pin_index_to_susi_iot_id_tuple(pin).pin_id
            except Exception as e:
                raise RuntimeError(f"Invalid pin index {pin}")
        else:
            raise TypeError(f"Invalid pin type : {type(pin)}")
        
        # Check if pin ID is in dict.
        found: bool = False
        for key, value in self.__dict_gpio_pin_ids.items():
            if value == pin_id:
                found = True
                break
        if not found:
            return None
        
        # Calculate GPIO direction ID and check if it is in GPIO ID tuple dict
        try:
            id_diff = pin_id.value - _SusiIotId.Gpio00.value  
            pin_dir_id = _SusiIotId(_SusiIotId.GpioDir00.value + id_diff)
            if not _SusiIotIdUtilities.gpio_check_dir_id_in_susi_iot_id_tuple(pin_dir_id):
                return None
        except ValueError:
            return None
        
        # Convert direction value.
        converted_dir = _SusiIotIdUtilities.gpio_direction_types_to_susi_iot_gpio_direction_type(dir)
        
        # Set GPIO direction
        self.__funcs.set_value(pin_dir_id, converted_dir.value)

    def gpio_get_level(self, pin: Union[str, int]) -> Union[GpioLevelTypes, None]:
        
        # Check feature support
        if not self.is_gpio_supported:
            raise RuntimeError(f"Feature not supported : GPIO")
        
        # Get pin id from parameter
        if isinstance(pin, str):
            if pin not in self.__dict_gpio_pin_ids:
                return None
            pin_id = self.__dict_gpio_pin_ids[pin]
        elif isinstance(pin, int):
            try:
                pin_id = _SusiIotIdUtilities.gpio_pin_index_to_susi_iot_id_tuple(pin).pin_id
            except Exception as e:
                return None
        else:
            raise TypeError(f"Invalid pin type : {type(pin)}")
        
        # Check if pin ID is in dict.
        found: bool = False
        for key, value in self.__dict_gpio_pin_ids.items():
            if value == pin_id:
                found = True
                break
        if not found:
            return None
        
        # Calculate GPIO level ID and check if GPIO level ID is in GPIO ID tuple dict.
        try:
            id_diff = pin_id.value - _SusiIotId.Gpio00.value
            pin_level_id = _SusiIotId(_SusiIotId.GpioLevel00.value + id_diff)
            if not _SusiIotIdUtilities.gpio_check_level_id_in_susi_iot_id_tuple(pin_level_id):
                return None
        except ValueError:
            return None
        
        # Get GPIO level
        data_json_obj = self.__funcs.get_data_by_id(pin_level_id)
        if 'bv' not in data_json_obj:
            return None
        try:
            level = _SusiIotGpioLevelType(data_json_obj['bv'])
        except ValueError:
            return None
        
        # Convert level type
        converted_level = _SusiIotIdUtilities.susi_iot_gpio_level_type_to_gpio_level_types(level)
        
        # Return value
        return converted_level

    def gpio_set_level(self, pin: Union[str, int], level: GpioLevelTypes) -> None:
        
        # Check feature support
        if not self.is_gpio_supported:
            raise RuntimeError(f"Feature not supported : GPIO")
        
        # Check if GPIO is in OUTPUT mode
        dir_value = self.gpio_get_direction(pin)
        if dir_value is None:
            raise RuntimeError(f"error : fail to get gpio direction for checking direction.")
        if dir_value != GpioDirectionTypes.Output:
            raise RuntimeError(f"error: set gpio level must in output, the direction is input now.")
        
        # Get pin id from parameter
        if isinstance(pin, str):
            if pin not in self.__dict_gpio_pin_ids:
                raise RuntimeError(f"Invalid pin name : {pin}")
            pin_id = self.__dict_gpio_pin_ids[pin]
        elif isinstance(pin, int):
            try:
                pin_id = _SusiIotIdUtilities.gpio_pin_index_to_susi_iot_id_tuple(pin).pin_id
            except Exception as e:
                raise RuntimeError(f"Invalid pin index {pin}")
        else:
            raise TypeError(f"Invalid pin type : {type(pin)}")
        
        # Calculate GPIO level ID and check if it is in GPIO ID tuple dict
        try:
            id_diff = pin_id.value - _SusiIotId.Gpio00.value
            pin_level_id = _SusiIotId(_SusiIotId.GpioLevel00.value + id_diff)
            if not _SusiIotIdUtilities.gpio_check_level_id_in_susi_iot_id_tuple(pin_level_id):
                return None
        except ValueError:
            return None
        
        # Convert direction value.
        converted_level = _SusiIotIdUtilities.gpio_level_types_to_susi_iot_gpio_level_type(level)
        
        # Set GPIO level
        self.__funcs.set_value(pin_level_id, converted_level.value)

    ################################################################

    # Feature : Watchdog
    
    @property
    def is_watchdog_supported(self) -> bool:
        return False
    
    @property
    def watchdog_timers(self) -> List[str]:
        return []

    def watchdog_start_timer(self, timer: Union[str, int], delay: int, event_timeout: int, reset_timeout: int) -> None:
        
        # Check feature support
        if not self.is_watchdog_supported:
            raise RuntimeError(f"Feature not supported : Watchdog")
        
        raise NotImplementedError("Watchdog timer is not supported in this version")
    
    def watchdog_stop_timer(self, timer: Union[str, int]) -> None:
        
        # Check feature support
        if not self.is_watchdog_supported:
            raise RuntimeError(f"Feature not supported : Watchdog")
        
        raise NotImplementedError("Watchdog timer is not supported in this version")
    
    def watchdog_trigger_timer(self, timer: Union[str, int]) -> None:
        
        # Check feature support
        if not self.is_watchdog_supported:
            raise RuntimeError(f"Feature not supported : Watchdog")
        
        raise NotImplementedError("Watchdog timer is not supported in this version")

    ################################################################

    # Feature : Memory

    @property
    def is_memory_supported(self) -> bool:
        return len(self.__dict_memory) > 0
    
    @property
    def memory_list(self) -> List[str]:
        return list(self.__dict_memory.keys())
    
    @property
    def memory_count(self) -> int:
        return len(self.__dict_memory)

    def memory_get_type(self, index = 0) -> Union[str, None]:
        
        try:
            id = _SusiIotId(_SusiIotId.SdramMemoryType0.value + index)
        except ValueError:
            return None
        
        data_json_obj = self.__funcs.get_data_by_id(id)
        if "sv" not in data_json_obj:
            return None
        
        return data_json_obj["sv"]

    def memory_get_module_type(self, index = 0) -> Union[str, None]:
        
        try:
            id = _SusiIotId(_SusiIotId.SdramMemoryModuleType0.value + index)
        except ValueError:
            return None
        
        data_json_obj = self.__funcs.get_data_by_id(id)
        if "sv" not in data_json_obj:
            return None
        
        return data_json_obj["sv"]

    def memory_get_size_in_GB(self, index = 0) -> Union[int, None]:
        
        try:
            id = _SusiIotId(_SusiIotId.SdramMemorySizeInGigaBytes0.value + index)
        except ValueError:
            return None
        
        data_json_obj = self.__funcs.get_data_by_id(id)
        if "v" not in data_json_obj:
            return None
        
        try:
            value = int(data_json_obj["v"])
        except (ValueError, TypeError):
            return None
        
        return value

    def memory_get_speed(self, index = 0) -> Union[str, None]:
        
        try:
            id = _SusiIotId(_SusiIotId.SdramMemorySpeed0.value + index)
        except ValueError:
            return None
        
        data_json_obj = self.__funcs.get_data_by_id(id)
        if "sv" not in data_json_obj:
            return None
        
        return data_json_obj["sv"]

    def memory_get_rank(self, index = 0) -> Union[int, None]:
        
        try:
            id = _SusiIotId(_SusiIotId.SdramMemoryRank0.value + index)
        except ValueError:
            return None
        
        data_json_obj = self.__funcs.get_data_by_id(id)
        if "v" not in data_json_obj:
            return None
        
        try:
            value = int(data_json_obj["v"])
        except (ValueError, TypeError):
            return None
        
        return value

    def memory_get_voltage(self, index = 0) -> Union[float, None]:
        
        try:
            id = _SusiIotId(_SusiIotId.SdramMemoryVoltage0.value + index)
        except ValueError:
            return None

        data_json_obj = self.__funcs.get_data_by_id(id)
        if "v" not in data_json_obj:
            return None
        
        try:
            value = float(data_json_obj["v"])
        except (ValueError, TypeError):
            return None
        
        return value

    def memory_get_bank(self, index = 0) -> Union[str, None]:
        
        try:
            id = _SusiIotId(_SusiIotId.SdramMemoryBank0.value + index)
        except ValueError:
            return None
        
        data_json_obj = self.__funcs.get_data_by_id(id)
        if "sv" not in data_json_obj:
            return None
        
        return data_json_obj["sv"]

    def memory_get_manufacturing_date_code(self, index = 0) -> Union[str, None]:
        
        try:
            id = _SusiIotId(_SusiIotId.SdramMemoryManufacturingDateCode0.value + index)
        except ValueError:
            return None
        
        data_json_obj = self.__funcs.get_data_by_id(id)
        if "sv" not in data_json_obj:
            return None
        
        return data_json_obj["sv"]

    def memory_get_temperature(self, index = 0) -> Union[float, None]:
        
        try:
            id = _SusiIotId(_SusiIotId.SdramMemoryTemperature0.value + index)
        except ValueError:
            return None
        
        data_json_obj = self.__funcs.get_data_by_id(id)
        if "v" not in data_json_obj:
            return None
        
        try:
            value = float(data_json_obj["v"])
        except (ValueError, TypeError):
            return None
        
        return value

    def memory_get_write_protection(self, index = 0) -> Union[str, None]:
        
        try:
            id = _SusiIotId(_SusiIotId.SdramMemoryWriteProtection0.value + index)
        except ValueError:
            return None
        
        data_json_obj = self.__funcs.get_data_by_id(id)
        if "sv" not in data_json_obj:
            return None
        
        return data_json_obj["sv"]

    def memory_get_module_manufacture(self, index = 0) -> Union[str, None]:
        
        try:
            id = _SusiIotId(_SusiIotId.SdramMemoryModuleManufacture0.value + index)
        except ValueError:
            return None
        
        data_json_obj = self.__funcs.get_data_by_id(id)
        if "sv" not in data_json_obj:
            return None
        
        return data_json_obj["sv"]

    def memory_get_manufacture(self, index = 0) -> Union[str, None]:
        
        try:
            id = _SusiIotId(_SusiIotId.SdramMemoryManufacture0.value + index)
        except ValueError:
            return None
        
        data_json_obj = self.__funcs.get_data_by_id(id)
        if "sv" not in data_json_obj:
            return None
        
        return data_json_obj["sv"]

    def memory_get_part_number(self, index = 0) -> Union[str, None]:
        
        try:
            id = _SusiIotId(_SusiIotId.SdramMemoryPartNumber0.value + index)
        except ValueError:
            return None
        
        data_json_obj = self.__funcs.get_data_by_id(id)
        if "sv" not in data_json_obj:
            return None
        
        return data_json_obj["sv"]

    def memory_get_specific(self, index = 0) -> Union[str, None]:
        
        try:
            id = _SusiIotId(_SusiIotId.SdramMemorySpecific0.value + index)
        except ValueError:
            return None
        
        data_json_obj = self.__funcs.get_data_by_id(id)
        if "sv" not in data_json_obj:
            return None
        
        return data_json_obj["sv"]
    
    ################################################################
    
    # Feature : Disk Info
    
    @property
    def is_disk_info_supported(self) -> bool:
        return len(self.__dict_disks) > 0
    
    @property
    def disk_info_disks(self) -> List[str]:
        return list(self.__dict_disks.keys())
    
    def disk_info_get_total_space(self, disk: Union[str, int]) -> Union[int, None]:
        
        # susi iot bug, there are two item with same id=353697792
        data_json_obj = self.__funcs.get_data_by_id(_SusiIotId.DiskInfoTotalDiskSpace)
        
        if isinstance(data_json_obj, dict):
            data_json_obj = data_json_obj['e'][0]
            return data_json_obj["v"]
        else:
            return data_json_obj["v"]
    
    def disk_info_get_free_space(self, disk: Union[str, int]) -> Union[int, None]:
        
        data_json_obj = self.__funcs.get_data_by_id(_SusiIotId.DiskInfoFreeDiskSpace)
        if "v" not in data_json_obj:
            return None
        
        try:
            value = int(data_json_obj["v"])
        except (ValueError, TypeError):
            return None
        
        return value