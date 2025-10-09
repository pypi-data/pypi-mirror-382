import threading
from typing import List
from typing import Tuple
from typing import Union
from typing import NamedTuple

from ._eapi_ids import _EApiIdUtilities

from ._eapi_functions import _EApiStatus, _EApiId, _EApiFunctions
from ._eapi_functions import EAPI_DECODE_HWMON_VALUE, EAPI_DECODE_CELCIUS, EAPI_CELCIUS_TO_FAHRENHEIT
from ._eapi_functions import EAPI_GPIO_GPIO_ID
from ._eapi_functions import _DiskInfoC, _DiskInfo, _DiskPartInfo

from ._eapi_gpio import _EApiGpioBitMaskStates, _EApiGpioDirectionType, _EApiGpioLevelType

from .._feature_provider._platform_info_data import DmiInfo, _PlatformInfoData

from ...ifeatures.ionboardsensors import TemperatureSources
from ...ifeatures.ionboardsensors import VoltageSources
from ...ifeatures.ionboardsensors import FanSources
from ...ifeatures.ionboardsensors import CurrentSources
from ...ifeatures.ionboardsensors import PowerSources

from ...ifeatures.igpio import GpioDirectionTypes, GpioLevelTypes

class WatchdogCap(NamedTuple):
    max_delay_in_ms: int
    max_event_timeout_in_ms: int
    max_reset_timeout_in_ms: int

class _EApi:

    ################################################################

    __instance = None
    __lock = threading.Lock()

    def __new__(cls):

        # Check library existence
        if _EApiFunctions.is_lib_exists() == False:
            raise ModuleNotFoundError("EApi")

        # Create instance
        with cls.__lock:
            if not cls.__instance:
                cls.__instance = super(_EApi, cls).__new__(cls)
            return cls.__instance

    def __init__(self):

        # Check if the class is already initialized
        if not hasattr(self, '_initialized'):

            # Initialize the flag
            self._initialized = True

            # Create EAPI instance
            self.__funcs = _EApiFunctions()

            # Get capability of feature : Platform Information
            self.__platform_data = self.__read_platform_information()

            # Get capability of feature : Onboard Sensors
            self.__onboard_sensors_temperature_ids = self.__read_onboard_sensors_ids(
                _EApiId.EAPI_ID_HWMON_TEMP_BASE,
                _EApiId.EAPI_ID_HWMON_TEMP_MAX
            )
            self.__onboard_sensors_voltage_ids = self.__read_onboard_sensors_ids(
                _EApiId.EAPI_ID_HWMON_VOLTAGE_BASE,
                _EApiId.EAPI_ID_HWMON_VOLTAGE_MAX
            )
            self.__onboard_sensors_fan_speed_ids = self.__read_onboard_sensors_ids(
                _EApiId.EAPI_ID_HWMON_FAN_BASE,
                _EApiId.EAPI_ID_HWMON_FAN_MAX
            )
            self.__onboard_sensors_current_ids = self.__read_onboard_sensors_ids(
                _EApiId.EAPI_ID_HWMON_CURRENT_BASE,
                _EApiId.EAPI_ID_HWMON_CURRENT_MAX
            )
            self.__onboard_sensors_power_ids = self.__read_onboard_sensors_ids(
                _EApiId.EAPI_ID_HWMON_POWER_BASE,
                _EApiId.EAPI_ID_HWMON_POWER_MAX
            )

            # Get capability of feature : GPIO
            status, gpio_count = self.__funcs.gpio_get_count()
            self.__gpio_count = gpio_count if status == _EApiStatus.SUCCESS else 0

            # Get capability of feature : Watchdog
            self.__watchdog_cap = self.__read_watchdog_cap()
    
    def __del__(self):
        
        if self.__funcs is not None:
            del self.__funcs

    ################################################################

    def __read_platform_information(self) -> Union[_PlatformInfoData, None]:

        # Read info : board
        status, board_info_str = self.__funcs.board_info_get_string(
            _EApiId.EAPI_ID_BOARD_NAME_STR)
        motherboard_name = board_info_str if status == _EApiStatus.SUCCESS else str()
        status, board_info_str = self.__funcs.board_info_get_string(
            _EApiId.EAPI_ID_BOARD_MANUFACTURER_STR)
        manufacturer = board_info_str if status == _EApiStatus.SUCCESS else str()
        status, board_info_str = self.__funcs.board_info_get_string(
            _EApiId.EAPI_ID_BOARD_REVISION_STR)
        revision = board_info_str if status == _EApiStatus.SUCCESS else str()
        status, board_info_str = self.__funcs.board_info_get_string(
            _EApiId.EAPI_ID_BOARD_SERIAL_STR)
        serial = board_info_str if status == _EApiStatus.SUCCESS else str()
        status, board_info_str = self.__funcs.board_info_get_string(
            _EApiId.EAPI_ID_BOARD_BIOS_REVISION_STR)
        bios_revision = board_info_str if status == _EApiStatus.SUCCESS else str()
        status, board_info_str = self.__funcs.board_info_get_string(
            _EApiId.EAPI_ID_BOARD_HW_REVISION_STR)
        hw_revision = board_info_str if status == _EApiStatus.SUCCESS else str()
        status, board_info_str = self.__funcs.board_info_get_string(
            _EApiId.EAPI_ID_BOARD_PLATFORM_TYPE_STR)
        platform_type = board_info_str if status == _EApiStatus.SUCCESS else str()
        status, board_info_str = self.__funcs.board_info_get_string(
            _EApiId.EAPI_ID_BOARD_EC_REVISION_STR)
        ec_revision = board_info_str if status == _EApiStatus.SUCCESS else str()
        status, board_info_str = self.__funcs.board_info_get_string(
            _EApiId.EAPI_ID_BOARD_OS_REVISION_STR)
        os_revision = board_info_str if status == _EApiStatus.SUCCESS else str()
        status, board_info_str = self.__funcs.board_info_get_string(
            _EApiId.EAPI_ID_BOARD_CPU_MODEL_NAME_STR)
        cpu_model_name = board_info_str if status == _EApiStatus.SUCCESS else str()
        
        # Read info : DMI
        status, board_info_str = self.__funcs.board_info_get_string(
            _EApiId.EAPI_ID_BOARD_DMIBIOS_VENDOR_STR)
        dmi_info_bios_vendor = board_info_str if status == _EApiStatus.SUCCESS else str()
        status, board_info_str = self.__funcs.board_info_get_string(
            _EApiId.EAPI_ID_BOARD_DMIBIOS_VERSION_STR)
        dmi_info_bios_version = board_info_str if status == _EApiStatus.SUCCESS else str()
        status, board_info_str = self.__funcs.board_info_get_string(
            _EApiId.EAPI_ID_BOARD_DMIBIOS_DATE_STR)
        dmi_info_bios_release_date = board_info_str if status == _EApiStatus.SUCCESS else str()
        status, board_info_str = self.__funcs.board_info_get_string(
            _EApiId.EAPI_ID_BOARD_DMISYS_UUID_STR)
        dmi_info_sys_uuid = board_info_str if status == _EApiStatus.SUCCESS else str()
        status, board_info_str = self.__funcs.board_info_get_string(
            _EApiId.EAPI_ID_BOARD_DMISYS_VENDOR_STR)
        dmi_info_sys_vendor = board_info_str if status == _EApiStatus.SUCCESS else str()
        status, board_info_str = self.__funcs.board_info_get_string(
            _EApiId.EAPI_ID_BOARD_DMISYS_PRODUCT_STR)
        dmi_info_sys_product = board_info_str if status == _EApiStatus.SUCCESS else str()
        status, board_info_str = self.__funcs.board_info_get_string(
            _EApiId.EAPI_ID_BOARD_DMISYS_VERSION_STR)
        dmi_info_sys_version = board_info_str if status == _EApiStatus.SUCCESS else str()
        status, board_info_str = self.__funcs.board_info_get_string(
            _EApiId.EAPI_ID_BOARD_DMISYS_SERIAL_STR)
        dmi_info_sys_serial = board_info_str if status == _EApiStatus.SUCCESS else str()
        status, board_info_str = self.__funcs.board_info_get_string(
            _EApiId.EAPI_ID_BOARD_DMIBOARD_VENDOR_STR)
        dmi_info_board_vendor = board_info_str if status == _EApiStatus.SUCCESS else str()
        status, board_info_str = self.__funcs.board_info_get_string(
            _EApiId.EAPI_ID_BOARD_DMIBOARD_NAME_STR)
        dmi_info_board_name = board_info_str if status == _EApiStatus.SUCCESS else str()
        status, board_info_str = self.__funcs.board_info_get_string(
            _EApiId.EAPI_ID_BOARD_DMIBOARD_VERSION_STR)
        dmi_info_board_version = board_info_str if status == _EApiStatus.SUCCESS else str()
        status, board_info_str = self.__funcs.board_info_get_string(
            _EApiId.EAPI_ID_BOARD_DMIBOARD_SERIAL_STR)
        dmi_info_board_serial = board_info_str if status == _EApiStatus.SUCCESS else str()
        status, board_info_str = self.__funcs.board_info_get_string(
            _EApiId.EAPI_ID_BOARD_DMIBOARD_ASSET_TAG_STR)
        dmi_info_board_asset_tag = board_info_str if status == _EApiStatus.SUCCESS else str()
        
        # Create DMI instance
        dmi_info = DmiInfo(
            bios_vendor=dmi_info_bios_vendor,
            bios_version=dmi_info_bios_version,
            bios_release_date=dmi_info_bios_release_date,
            sys_uuid=dmi_info_sys_uuid,
            sys_vendor=dmi_info_sys_vendor,
            sys_product=dmi_info_sys_product,
            sys_version=dmi_info_sys_version,
            sys_serial=dmi_info_sys_serial,
            board_vendor=dmi_info_board_vendor,
            board_name=dmi_info_board_name,
            board_version=dmi_info_board_version,
            board_serial=dmi_info_board_serial,
            board_asset_tag=dmi_info_board_asset_tag
        )

        return _PlatformInfoData(
            motherboard_name=motherboard_name,
            manufacturer=manufacturer,
            boot_up_times=None,
            running_time_in_hours=None,
            bios_revision=bios_revision,
            firmware_name=None,
            firmware_version=None,
            library_version=None,
            driver_version=None,
            ec_revision=ec_revision,
            dmi_info=dmi_info
        )

    def __read_onboard_sensors_ids(self, base: _EApiId, max: _EApiId) -> List[_EApiId]:
        
        # Create ID list from enum
        ids: List[_EApiId] = [_EApiId(base.value + i) for i in range(max.value)]
        
        # Try to get board value. If success, add ID to returned list
        id_list: List[_EApiId] = []
        for id in ids:
            status, board_info_value = self.__funcs.board_info_get_value(id)
            if status == _EApiStatus.SUCCESS:
                id_list.append(id)
        
        return id_list

    def __read_watchdog_cap(self) -> Union[WatchdogCap, None]:
        
        status, max_delay, max_event_timeout, max_reset_timeout = self.__funcs.watchdog_get_cap()
        watchdog_cap = WatchdogCap(max_delay, max_event_timeout, max_reset_timeout) \
            if status == _EApiStatus.SUCCESS and \
                max_delay is not None and \
                max_event_timeout is not None and \
                max_reset_timeout is not None \
            else None
        
        return watchdog_cap

    ################################################################
    
    def __gpio_to_pin_id(self, pin: Union[str, int]) -> Union[int, None]:
        
        if isinstance(pin, str):
            try:
                pin_int = int(pin)
            except ValueError:
                return None
        elif isinstance(pin, int):
            pin_int = pin
        else:
            return None
        
        pin_int = EAPI_GPIO_GPIO_ID(pin_int)
        
        return pin_int
    
    def __gpio_check_pin_valid(self, pin: int) -> Tuple[bool, str]:
        
        err_msg = ""
        
        # Check if specified pin index is out of range.
        if self.__gpio_count is None:
            err_msg = f"GPIO count is None"
            return False, err_msg
        if pin >= self.__gpio_count:
            err_msg = f"GPIO index out of range. Index: {pin}"
            return False, err_msg
        
        return True, err_msg

    ################################################################
    
    # Check library existence
    
    @classmethod
    def is_lib_exists(cls) -> bool:
        return _EApiFunctions.is_lib_exists()

    ################################################################

    # Feature : Platform Information

    @property
    def is_platform_information_supported(self) -> bool:
        return self.__platform_data != None

    @property
    def platform_info_data(self) -> _PlatformInfoData:
        
        if self.__platform_data is None:
            raise RuntimeError("Platform Information feature is not supported")
        
        return self.__platform_data

    ################################################################

    # Feature : Onboard Sensors

    @property
    def is_onboard_sensors_supported(self) -> bool:
        length = 0
        length += len(self.__onboard_sensors_temperature_ids)
        length += len(self.__onboard_sensors_voltage_ids)
        length += len(self.__onboard_sensors_fan_speed_ids)
        length += len(self.__onboard_sensors_current_ids)
        length += len(self.__onboard_sensors_power_ids)
        return length > 0

    @property
    def onboard_sensors_temperature_sources(self) -> List[str]:
        return [id.name for id in self.__onboard_sensors_temperature_ids] 

    def onboard_sensors_get_temperature(self, src: Union[str, TemperatureSources]) -> Union[float, None]:
        
        # Convert src to ID
        if isinstance(src, str):
            try:
                id = _EApiId[src]
            except KeyError:
                return None
        elif isinstance(src, TemperatureSources):
            try:
                id = _EApiIdUtilities.temperature_sources_to_eapi_id(src)
            except Exception as e:
                return None
        else:
            return None
        
        # Check if specified ID is in list.
        if id not in self.__onboard_sensors_temperature_ids:
            return None
        
        # Get board value
        status, board_info_value = self.__funcs.board_info_get_value(id)
        if status != _EApiStatus.SUCCESS or board_info_value is None:
            return None
        
        # Convert raw data to displayed data.
        celcius = EAPI_DECODE_CELCIUS(board_info_value)
        fahrenheit = EAPI_CELCIUS_TO_FAHRENHEIT(celcius)

        return celcius

    @property
    def onboard_sensors_voltage_sources(self) -> List[str]:
        return [id.name for id in self.__onboard_sensors_voltage_ids]

    def onboard_sensors_get_voltage(self, src: Union[str, VoltageSources]) -> Union[float, None]:
        
        # Convert src to ID
        if isinstance(src, str):
            try:
                id = _EApiId[src]
            except KeyError:
                return None
        elif isinstance(src, VoltageSources):
            try:
                id = _EApiIdUtilities.voltage_sources_to_eapi_id(src)
            except Exception as e:
                return None
        else:
            return None
        
        # Check if specified ID is in list.
        if id not in self.__onboard_sensors_voltage_ids:
            return None
        
        # Get board value
        status, board_info_value = self.__funcs.board_info_get_value(id)
        if status != _EApiStatus.SUCCESS or board_info_value is None:
            return None
        
        # Convert raw data to displayed data.
        volts = EAPI_DECODE_HWMON_VALUE(board_info_value)

        return volts   

    @property
    def onboard_sensors_fan_sources(self) -> List[str]:
        return [id.name for id in self.__onboard_sensors_fan_speed_ids]

    def onboard_sensors_get_fan_speed(self, src: Union[str, FanSources]) -> Union[float, None]:
        
        # Convert src to ID
        if isinstance(src, str):
            try:
                id = _EApiId[src]
            except KeyError:
                return None
        elif isinstance(src, FanSources):
            try:
                id = _EApiIdUtilities.fan_sources_to_eapi_id(src)
            except Exception as e:
                return None
        else:
            return None
        
        # Check if specified ID is in list.
        if id not in self.__onboard_sensors_voltage_ids:
            return None
        
        # Get board value
        status, board_info_value = self.__funcs.board_info_get_value(id)
        if status != _EApiStatus.SUCCESS or board_info_value is None:
            return None
        
        # Convert raw data to displayed data.
        rpm = EAPI_DECODE_HWMON_VALUE(board_info_value)

        return rpm

    ################################################################

    # Feature : GPIO

    @property
    def is_gpio_supported(self) -> bool:
        return self.__gpio_count > 0 if self.__gpio_count != None else False

    @property
    def gpio_pins(self) -> List[str]:
        if self.__gpio_count is None:
            return []
        return [f"{id}" for id in range(self.__gpio_count)] 

    @property
    def gpio_max_pin_num(self) -> int:
        return self.__gpio_count if self.__gpio_count != None else 0

    def gpio_get_direction(self, pin: Union[str, int]) -> Union[GpioDirectionTypes, None]:
        
        # Check feature support
        if not self.is_gpio_supported:
            raise RuntimeError(f"Feature not supported : GPIO")
        
        # Convert pin to pin ID
        pin_id = self.__gpio_to_pin_id(pin)
        if pin_id is None:
            return None
        
        # Check if specified pin index is out of range.
        is_pin_valid, err_msg = self.__gpio_check_pin_valid(pin_id)
        if not is_pin_valid:
            return None
        
        # Get GPIO direction
        status, dir = self.__funcs.gpio_get_direction(pin_id)
        if status != _EApiStatus.SUCCESS or dir is None:
            return None
        
        # Convert direction type
        ret_dir = _EApiIdUtilities.eapi_gpio_direction_type_to_gpio_direction_types(dir)
        
        return ret_dir

    def gpio_set_direction(self, pin: Union[str, int], dir: GpioDirectionTypes) -> None:
        
        # Check feature support
        if not self.is_gpio_supported:
            raise RuntimeError(f"Feature not supported : GPIO")
        
        # Convert pin to pin ID
        pin_id = self.__gpio_to_pin_id(pin)
        if pin_id is None:
            raise RuntimeError(f"Fail to conver pin to pin ID. Pin : {pin}")
        
        # Check if specified pin index is out of range.
        is_pin_valid, err_msg = self.__gpio_check_pin_valid(pin_id)
        if not is_pin_valid:
            raise RuntimeError(err_msg)
        
        # Convert direction type
        set_dir = _EApiIdUtilities.gpio_direction_types_to_eapi_gpio_direction_type(dir)
        
        # Set GPIO direction
        status = self.__funcs.gpio_set_direction(pin_id, set_dir)
        if status != _EApiStatus.SUCCESS:
            raise RuntimeError(f"Fail to set GPIO direction. Pin : {pin}. Direction : {dir}")

    def gpio_get_level(self, pin: Union[str, int]) -> Union[GpioLevelTypes, None]:
        
        # Check feature support
        if not self.is_gpio_supported:
            raise RuntimeError(f"Feature not supported : GPIO")
        
        # Convert pin to pin ID
        pin_id = self.__gpio_to_pin_id(pin)
        if pin_id is None:
            return None
        
        # Check if specified pin index is out of range.
        is_pin_valid, err_msg = self.__gpio_check_pin_valid(pin_id)
        if not is_pin_valid:
            return None
        
        # Get GPIO level
        status, level = self.__funcs.gpio_get_level(pin_id)
        if status != _EApiStatus.SUCCESS or level is None:
            return None
        
        # Convert level type
        ret_level = _EApiIdUtilities.eapi_gpio_level_type_to_gpio_level_types(level)

        return ret_level

    def gpio_set_level(self, pin: Union[str, int], level: GpioLevelTypes) -> None:
        
        # Check feature support
        if not self.is_gpio_supported:
            raise RuntimeError(f"Feature not supported : GPIO")
        
        # Convert pin to pin ID
        pin_id = self.__gpio_to_pin_id(pin)
        if pin_id is None:
            raise RuntimeError(f"Fail to conver pin to pin ID. Pin : {pin}")
        
        # Check if specified pin index is out of range.
        is_pin_valid, err_msg = self.__gpio_check_pin_valid(pin_id)
        if not is_pin_valid:
            raise RuntimeError(err_msg)
        
        # Check if pin is in OUTPUT mode.
        status, dir = self.__funcs.gpio_get_direction(pin_id)
        if status != _EApiStatus.SUCCESS or dir == None:
            raise RuntimeError(f"Fail to check GPIO direction before setting level. Pin : {pin}.")
        if dir != _EApiGpioDirectionType.EAPI_GPIO_OUTPUT:
            raise RuntimeError(f"Cannot set level of GPIO not in OUTPUT mode. Pin : {pin}.")
        
        # Convert level type
        set_level = _EApiIdUtilities.gpio_level_types_to_eapi_gpio_level_type(level)
        
        # Set GPIO level
        status = self.__funcs.gpio_set_level(pin_id, set_level)
        if status != _EApiStatus.SUCCESS:
            raise RuntimeError(f"Fail to set GPIO level. Pin : {pin}. Level : {level}")

    ################################################################

    # Feature : Watchdog

    @property
    def is_watchdog_supported(self) -> bool:
        return self.__watchdog_cap != None

    @property
    def watchdog_timers(self) -> List[str]:
        return [ "Timer0" ]
    
    @property
    def watchdog_cap(self) -> Union[WatchdogCap, None]:
        return self.__watchdog_cap

    def watchdog_start_timer(self, timer: Union[str, int], delay: int, event_timeout: int, reset_timeout: int) -> None:
        
        if self.__watchdog_cap is None:
            raise RuntimeError(f"Feature not supported : Watchdog")
        
        if (delay > self.__watchdog_cap.max_delay_in_ms):
            raise ValueError(f"Parameter out of range. Name : delay. Value : {delay}. Max : {self.__watchdog_cap.max_delay_in_ms}")
        if (event_timeout > self.__watchdog_cap.max_event_timeout_in_ms):
            raise ValueError(f"Parameter out of range. Name : event_timeout. Value : {event_timeout}. Max : {self.__watchdog_cap.max_event_timeout_in_ms}")
        if (reset_timeout > self.__watchdog_cap.max_reset_timeout_in_ms):
            raise ValueError(f"Parameter out of range. Name : reset_timeout. Value : {reset_timeout}. Max : {self.__watchdog_cap.max_reset_timeout_in_ms}")
        
        status = self.__funcs.watchdog_start(delay, event_timeout, reset_timeout)
        
        if status != _EApiStatus.SUCCESS:
            raise RuntimeError(f"Fail to start watchdog timer. Status : {status}")

    def watchdog_trigger_timer(self, timer: Union[str, int]) -> None:
        
        if not self.is_watchdog_supported:
            raise RuntimeError(f"Feature not supported : Watchdog")
        
        status = self.__funcs.watchdog_trigger()
        if status != _EApiStatus.SUCCESS:
            raise RuntimeError(f"Fail to stop trigger timer. Status : {status}")

    def watchdog_stop_timer(self, timer: Union[str, int]) -> None:
        
        if not self.is_watchdog_supported:
            raise RuntimeError(f"Feature not supported : Watchdog")
        
        status = self.__funcs.watchdog_stop()
        if status != _EApiStatus.SUCCESS:
            raise RuntimeError(f"Fail to stop watchdog timer. Status : {status}")

################################################################

    # Feature : Memory
    
    @property
    def is_memory_supported(self) -> bool:
        return False

    @property
    def memory_count(self) -> int:
        return 0

    def memory_get_type(self, index: int) -> Union[str, None]:
        return None

    def memory_get_module_type(self, index: int) -> Union[str, None]:
        return None

    def memory_get_size_in_GB(self, index: int) -> Union[int, None]:
        return None

    def memory_get_speed(self, index: int) -> Union[str, None]:
        return None

    def memory_get_rank(self, index: int) -> Union[int, None]:
        return None

    def memory_get_voltage(self, index: int) -> Union[float, None]:
        return None

    def memory_get_bank(self, index: int) -> Union[str, None]:
        return None

    def memory_get_manufacturing_date_code(self, index: int) -> Union[str, None]:
        return None

    def memory_get_temperature(self, index: int) -> Union[float, None]:
        return None

    def memory_get_write_protection(self, index: int) -> Union[str, None]:
        return None

    def memory_get_module_manufacture(self, index: int) -> Union[str, None]:
        return None

    def memory_get_manufacture(self, index: int) -> Union[str, None]:
        return None

    def memory_get_part_number(self, index: int) -> Union[str, None]:
        return None
    
    def memory_get_specific(self, index: int) -> Union[str, None]:
        return None
    
    ################################################################
    
    # Feature : Disk Information
    
    @property
    def is_disk_info_supported(self) -> bool:
        return False
    
    @property
    def disk_info_disks(self) -> List[str]:
        return []
    
    def disk_info_get_total_space(self, disk: Union[str, int]) -> Union[int, None]:
        return None
    
    def disk_info_get_free_space(self, disk: Union[str, int]) -> Union[int, None]:
        return None