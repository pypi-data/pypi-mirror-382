import threading
import os
import platform

from typing import List
from typing import Union
from typing import Tuple

from ctypes import RTLD_GLOBAL
from ctypes import CDLL
from ctypes import c_int
from ctypes import c_uint32
from ctypes import c_float
from ctypes import c_char_p
from ctypes import POINTER
from ctypes import pointer
from ctypes import CFUNCTYPE
from ctypes import create_string_buffer
from ctypes import byref

from ._eapi_status import _EApiStatus
from ._eapi_ids import _EApiId
from ._eapi_gpio import _EApiGpioBitMaskStates, _EApiGpioDirectionType, _EApiGpioLevelType

from ._eapi_etp import _ETP_USER_DATA, _ETP_DATA
from ._eapi_disk_info import _DiskInfo, _DiskInfoC, _DiskPartInfo

class _EApiFunctions:
    
    ################################################################
    
    __arch = platform.machine().lower()
    __os_name = platform.system()
    __path_lib = ""
    
    @classmethod
    def __lib_path_init(cls):
        
        try:
            
            # Get class members
            arch = cls.__arch
            os_name = cls.__os_name
            
            if os_name == "Linux" and 'x86' in arch:
                cls.__path_lib = "/lib/libEAPI.so"
            elif os_name == "Linux" and 'aarch64' in arch:
                cls.__path_lib = "/lib/libEAPI.so"
            elif os_name == "Windows" and 'x86' in arch:
                raise NotImplementedError(f"")
            elif os_name == "Windows" and 'aarch64' in arch:
                raise NotImplementedError(f"")
            else:
                raise ModuleNotFoundError(f"disable to import library, architechture:{arch}, os:{os_name}")

            # Check if library files exist.
            if not os.path.exists(cls.__path_lib):
                raise ModuleNotFoundError(path = cls.__path_lib)
            
        except ModuleNotFoundError as e:
            raise e
        
    @classmethod
    def is_lib_exists(cls) -> bool:
        
        # If init of library info succeeds, lib exists.
        try:
            cls.__lib_path_init()
            return True
        except ModuleNotFoundError as e:
            return False
        
    def __load_platform_sdk_lib(self):

        # Load the library with global symbols
        self.__lib_eapi = CDLL(self.__class__.__path_lib, RTLD_GLOBAL)
        
        # Define the function prototypes and return types

        prototype = CFUNCTYPE(
            c_uint32        # Return type : EApiStatus_t
        )
        self.__EApiLibInitialize = prototype(("EApiLibInitialize", self.__lib_eapi))

        prototype = CFUNCTYPE(
            c_uint32        # Return type : EApiStatus_t
        )
        self.__EApiLibUnInitialize = prototype(("EApiLibUnInitialize", self.__lib_eapi))
        
        prototype = CFUNCTYPE(
            c_uint32,               # Return type : EApiStatus_t
            c_uint32,               # Parameter 1 : EApiId_t (uint32_t)
            c_char_p,               # Parameter 2 : char *pValue
            POINTER(c_uint32)       # Parameter 3 : uint32_t *pBufLen
        )
        self.__EApiBoardGetStringA = prototype(("EApiBoardGetStringA", self.__lib_eapi))

        prototype = CFUNCTYPE(
            c_uint32,               # Return type : EApiStatus_t
            c_uint32,               # Parameter 1 : EApiId_t (uint32_t)
            POINTER(c_uint32)       # Parameter 2 : uint32_t *pValue
        )
        self.__EApiBoardGetValue = prototype(("EApiBoardGetValue", self.__lib_eapi))

        prototype = CFUNCTYPE(
            c_uint32,               # Return type : EApiStatus_t
            POINTER(c_uint32)       # Parameter 1 : uint32_t *pCount
        )
        self.__EApiGPIOGetCount = prototype(("EApiGPIOGetCount", self.__lib_eapi))

        prototype = CFUNCTYPE(
            c_uint32,               # Return type : EApiStatus_t
            c_uint32,               # Parameter 1 : EApiId_t (uint32_t)
            POINTER(c_uint32),      # Parameter 2 : uint32_t *pGpioInput
            POINTER(c_uint32)       # Parameter 3 : uint32_t *pGpioOutput
        )
        self.__EApiGPIOGetDirectionCaps = prototype(("EApiGPIOGetDirectionCaps", self.__lib_eapi))

        prototype = CFUNCTYPE(
            c_uint32,           # Return type : EApiStatus_t
            c_uint32,           # Parameter 1 : EApiId_t (uint32_t)
            c_uint32,           # Parameter 2 : uint32_t BitMask
            POINTER(c_uint32)   # Parameter 3 : uint32_t *pDirection
        )
        self.__EApiGPIOGetDirection = prototype(("EApiGPIOGetDirection", self.__lib_eapi))

        prototype = CFUNCTYPE(
            c_uint32,       # Return type : EApiStatus_t
            c_uint32,       # Parameter 1 : EApiId_t (uint32_t)
            c_uint32,       # Parameter 2 : uint32_t BitMask
            c_uint32        # Parameter 3 : uint32_t Direction
        )
        self.__EApiGPIOSetDirection = prototype(("EApiGPIOSetDirection", self.__lib_eapi))

        prototype = CFUNCTYPE(
            c_uint32,           # Return type : EApiStatus_t
            c_uint32,           # Parameter 1 : EApiId_t (uint32_t)
            c_uint32,           # Parameter 2 : uint32_t BitMask
            POINTER(c_uint32)   # Parameter 3 : uint32_t *pLevel
        )
        self.__EApiGPIOGetLevel = prototype(("EApiGPIOGetLevel", self.__lib_eapi))

        prototype = CFUNCTYPE(
            c_uint32,       # Return type : EApiStatus_t
            c_uint32,       # Parameter 1 : EApiId_t (uint32_t)
            c_uint32,       # Parameter 2 : uint32_t BitMask
            c_uint32        # Parameter 3 : uint32_t Level
        )
        self.__EApiGPIOSetLevel = prototype(("EApiGPIOSetLevel", self.__lib_eapi))

        prototype = CFUNCTYPE(
            c_uint32,           # Return type : EApiStatus_t
            POINTER(c_uint32),  # Parameter 1 : uint32_t *pMaxDelayInMilliseconds
            POINTER(c_uint32),  # Parameter 2 : uint32_t *pMaxEventTimeoutInMilliseconds
            POINTER(c_uint32)   # Parameter 3 : uint32_t *pMaxResetTimeoutInMilliseconds
        )
        self.__EApiWDogGetCap = prototype(("EApiWDogGetCap", self.__lib_eapi))
        
        prototype = CFUNCTYPE(
            c_uint32,           # Return type : EApiStatus_t
            c_uint32,           # Parameter 1 : uint32_t Delay
            c_uint32,           # Parameter 2 : uint32_t EventTimeout
            c_uint32            # Parameter 3 : uint32_t ResetTimeout
        )
        self.__EApiWDogStart = prototype(("EApiWDogStart", self.__lib_eapi))
        
        prototype = CFUNCTYPE(
            c_uint32            # Return type : EApiStatus_t
        )
        self.__EApiWDogTrigger = prototype(("EApiWDogTrigger", self.__lib_eapi))
        
        prototype = CFUNCTYPE(
            c_uint32            # Return type : EApiStatus_t
        )
        self.__EApiWDogStop = prototype(("EApiWDogStop", self.__lib_eapi))
        
        prototype = CFUNCTYPE(
            c_uint32,           # Return type : EApiStatus_t
            POINTER(c_float)    # Parameter 1 : float *pAvailableMemory
        )
        self.__EApiGetMemoryAvailable = prototype(("EApiGetMemoryAvailable", self.__lib_eapi))

        prototype = CFUNCTYPE(
            c_uint32,               # Return type : EApiStatus_t
            POINTER(_DiskInfoC)     # Parameter 1 : DiskInfo_t *pDiskInfo
        )
        self.__EApiGetDiskInfo = prototype(("EApiGetDiskInfo", self.__lib_eapi))

        prototype = CFUNCTYPE(
            c_uint32,                           # Return type : EApiStatus_t
            POINTER(POINTER(_ETP_USER_DATA))    # Parameter 1 : ETP_USER_DATA **pUserData
        )
        self.__EApiETPReadDeviceData = prototype(("EApiETPReadDeviceData", self.__lib_eapi))

        prototype = CFUNCTYPE(
            c_uint32,                           # Return type : EApiStatus_t
            POINTER(POINTER(_ETP_USER_DATA))    # Parameter 1 : ETP_USER_DATA **pUserData
        )
        self.__EApiETPReadUserData = prototype(("EApiETPReadUserData", self.__lib_eapi))

        prototype = CFUNCTYPE(
            c_uint32,               # Return type : EApiStatus_t
            c_uint32,               # Parameter 1 : EApiId_t (uint32_t)
            POINTER(c_uint32)       # Parameter 2 : uint32_t *pStatus
        )
        self.__EApiExtFunctionGetStatus = prototype(("EApiExtFunctionGetStatus", self.__lib_eapi))

        prototype = CFUNCTYPE(
            c_uint32,           # Return type : EApiStatus_t
            c_uint32,           # Parameter 1 : EApiId_t (uint32_t)
            c_uint32            # Parameter 2 : uint32_t status
        )
        self.__EApiExtFunctionSetStatus = prototype(("EApiExtFunctionSetStatus", self.__lib_eapi))
        
    ################################################################
    
    __instance = None
    __lock = threading.Lock()

    def __new__(cls):

        # Initialize library information
        cls.__lib_path_init()

        # Create instance
        with cls.__lock:
            if not cls.__instance:
                cls.__instance = super(_EApiFunctions, cls).__new__(cls)
            return cls.__instance

    def __init__(self):

        # Check if the class is already initialized
        if not hasattr(self, '_initialized'):

            # Initialize the flag
            self._initialized = True

            # Load libraries
            self.__load_platform_sdk_lib()

            # Call PlatformSDK function : EApiLibInitialize 
            status_value: int = self.__EApiLibInitialize()
            try:
                status = _EApiStatus(status_value)
                # Note : status code UNSUPPORTED, so comment checking logic
                # if status != _EApiStatus.SUCCESS:
                #     print(f"Fail to initialize EAPI. Status : {status}")
                #     exit()
            except ValueError:
                print(f"Fail to initialize EAPI. Status value : {status_value}")
                exit()
            
            # 生成 LED ID 列表
            led_min = _EApiId.EAPI_ID_EXT_FUNC_LED_MIN.value   # LED ID 範圍的最小值
            led_max = _EApiId.EAPI_ID_EXT_FUNC_LED_MAX.value   # LED ID 範圍的最大值
            self.__led_id_list = [led_min + i for i in range(led_max - led_min + 1)]

    def __del__(self):
        
        # Check if the class is already initialized
        if self.__class__.__instance is not None:

            # Call PlatformSDK function : EApiLibUnInitialize
            #status_value: int = self.__EApiLibUnInitialize()
            # try:
            #     status = _EApiStatus(status_value)
            #     if status != _EApiStatus.SUCCESS:
            #         print(f"Fail to uninitialize EAPI. Status : {status}")
            #         exit()
            # except ValueError:
            #     print(f"Fail to uninitialize EAPI. Status value : {status_value}")
            #     exit()

            # Set instance to None
            self.__class__.__instance = None

    ################################################################

    def _handle_error_code(self, n):
        n = int(n)
        if n < 0:
            n = (1 << 32) + n
        n = hex(n)
        if n == "0xfffff0ff":
            return "EAPI_STATUS_ERROR, Generic error"
        elif n == "0xfffffcff":
            return "EAPI_STATUS_UNSUPPORTED"
    
    ################################################################
    
    # Feature : Board information
    
    def board_info_get_string(self, id: _EApiId) -> Tuple[_EApiStatus, str]:
        
        CMD_RETURN_BUF_SIZE = 4096
        pValue = create_string_buffer(CMD_RETURN_BUF_SIZE)
        pBufLen = c_uint32(CMD_RETURN_BUF_SIZE)
        id_uint32 = c_uint32(id.value)
        
        status_value = self.__EApiBoardGetStringA(id_uint32, pValue, byref(pBufLen))
        
        try:
            status = _EApiStatus(status_value)
            if status != _EApiStatus.SUCCESS:
                return status, str()
        except ValueError:
            print(f"Unknown status value : {status_value}")
            exit()
        
        board_info_string = bytes(pValue).decode('utf-8') if status == _EApiStatus.SUCCESS else str()
        return status, board_info_string

    def board_info_get_value(self, id: _EApiId) -> Tuple[_EApiStatus, Union[int, None]]:
            
        pValue = c_uint32(0)
        id_uint32 = c_uint32(id.value)
        
        status_value = self.__EApiBoardGetValue(id_uint32, byref(pValue))
        
        try:
            status = _EApiStatus(status_value)
            if status != _EApiStatus.SUCCESS:
                return status, None
        except ValueError:
            print(f"Unknown status value : {status_value}")
            exit()
        
        board_info_value = pValue.value
        return status, board_info_value
        
    def board_info_get_available_memory(self) -> Tuple[_EApiStatus, Union[float, None]]:
        """
        Get the available memory on the board (KB).
        """
        
        available_memory_float = c_float(0.0)
        
        status_value = self.__EApiGetMemoryAvailable(byref(available_memory_float))
        
        try:
            status = _EApiStatus(status_value)
            if status != _EApiStatus.SUCCESS:
                return status, None
        except ValueError:
            print(f"Unknown EAPI status value : {status_value}")
            exit()
        
        available_memory = available_memory_float.value
        return status, available_memory
    
    def board_info_get_disk_info(self) -> Tuple[_EApiStatus, Union[_DiskInfo, None]]:
        """
        Get disk information from the board.
        """
        
        disk_info_c = _DiskInfoC()
        
        status_value = self.__EApiGetDiskInfo(byref(disk_info_c))
        
        try:
            status = _EApiStatus(status_value)
            if status != _EApiStatus.SUCCESS:
                return status, None
        except ValueError:
            print(f"Unknown EAPI status value : {status_value}")
            exit()
        
        disk_info_obj = _DiskInfo(
            disk_count = disk_info_c.disk_count,
            disk_part_info = [
                _DiskPartInfo(
                    partition_id=disk_info_c.disk_part_info[i].partition_id,
                    partition_size=disk_info_c.disk_part_info[i].partition_size,
                    partition_name=disk_info_c.disk_part_info[i].partition_name.decode("utf-8")
                ) for i in range(disk_info_c.disk_count)
            ]
        ) if status == _EApiStatus.SUCCESS else None
        return status, disk_info_obj
    
    ################################################################
    
    # Feature : GPIO
    
    def gpio_get_count(self) -> Tuple[_EApiStatus, Union[int, None]]:
        
        count_uint32 = c_uint32()
        
        status_value: int = self.__EApiGPIOGetCount(byref(count_uint32))
        
        try:
            status = _EApiStatus(status_value)
            if status != _EApiStatus.SUCCESS:
                return status, None
        except ValueError:
            print(f"Unknown status value : {status_value}")
            exit()
        
        count = count_uint32.value
        return status, count

    def gpio_get_dir_cap(self, id: int) -> Tuple[_EApiStatus, Union[int, None], Union[int, None]]:
        """
        Get the direction capabilities of a GPIO pin.
        """
        
        id_uint32 = c_uint32(id)
        input_uint32 = c_uint32()
        output_uint32 = c_uint32()
        
        status_value: int = self.__EApiGPIOGetDirectionCaps(id_uint32, byref(input_uint32), byref(output_uint32))
        
        try:
            status = _EApiStatus(status_value)
            if status != _EApiStatus.SUCCESS:
                return status, None, None
        except ValueError:
            print(f"Unknown status value : {status_value}")
            exit()

        return status, input_uint32.value, output_uint32.value

    def gpio_get_direction(self, id: int) -> Tuple[_EApiStatus, Union[_EApiGpioDirectionType, None]]:
        """
        Get the direction of a GPIO pin.
        """
        
        id_uint32 = c_uint32(id)
        bitmask_uint32 = c_uint32(_EApiGpioBitMaskStates.EAPI_GPIO_BITMASK_SELECT.value)
        dir_uint32 = c_uint32()
        
        status_value: int = self.__EApiGPIOGetDirection(id_uint32, bitmask_uint32, byref(dir_uint32))
        
        try:
            status = _EApiStatus(status_value)
            if status != _EApiStatus.SUCCESS:
                return status, None
        except ValueError:
            print(f"Unknown status value : {status_value}")
            exit()
        
        try:
            dir = _EApiGpioDirectionType(dir_uint32.value)
        except ValueError:
            print(f"Unknown direction value {dir_uint32.value}")
            exit()
        
        return status, dir

    def gpio_set_direction(self, id: int, dir: _EApiGpioDirectionType) -> _EApiStatus:
        """
        Set the direction of a GPIO pin.
        """
        
        id_uint32 = c_uint32(id)
        bitmask_uint32 = c_uint32(_EApiGpioBitMaskStates.EAPI_GPIO_BITMASK_SELECT.value)
        dir_uint32 = c_uint32(dir.value)
        
        status_value: int = self.__EApiGPIOSetDirection(id_uint32, bitmask_uint32, dir_uint32)
        
        try:
            status = _EApiStatus(status_value)
        except ValueError:
            print(f"Unknown EAPI status value : {status_value}")
            exit()
            
        return status
    
    def gpio_get_level(self, id: int) -> Tuple[_EApiStatus, Union[_EApiGpioLevelType, None]]:
        """
        Get the level of a GPIO pin.
        """
        
        id_uint32 = c_uint32(id)
        bitmask_uint32 = c_uint32(_EApiGpioBitMaskStates.EAPI_GPIO_BITMASK_SELECT.value)
        level_uint32 = c_uint32()
        
        status_value: int = self.__EApiGPIOGetLevel(id_uint32, bitmask_uint32, byref(level_uint32))
        
        try:
            status = _EApiStatus(status_value)
            if status != _EApiStatus.SUCCESS:
                return status, None
        except ValueError:
            print(f"Unknown status value : {status_value}")
            exit()
            
        try:
            level = _EApiGpioLevelType(level_uint32.value)
        except ValueError:
            print(f"Unknown level value {level_uint32.value}")
            exit()

        return status, level

    def gpio_set_level(self, id: int, level: _EApiGpioLevelType) -> _EApiStatus:
        """
        Set the level of a GPIO pin.
        """
        
        id_uint32 = c_uint32(id)
        bitmask_uint32 = c_uint32(_EApiGpioBitMaskStates.EAPI_GPIO_BITMASK_SELECT.value)
        level_uint32 = c_uint32(level.value)
        
        status_value: int = self.__EApiGPIOSetLevel(id_uint32, bitmask_uint32, level_uint32)
        
        try:
            status = _EApiStatus(status_value)
        except ValueError:
            print(f"Unknown EAPI status value : {status_value}")
            exit()

        return status
        
    ################################################################
    
    # Feature : Watchdog
    
    def watchdog_get_cap(self) -> Tuple[_EApiStatus, Union[int, None], Union[int, None], Union[int, None]]:
        """
        Get the capabilities of the watchdog timer.
        """
        
        max_delay_uint32 = c_uint32(0)
        max_event_timeout_uint32 = c_uint32(0)
        max_reset_timeout_uint32 = c_uint32(0)
        
        status_value: int = self.__EApiWDogGetCap(
            byref(max_delay_uint32),
            byref(max_event_timeout_uint32),
            byref(max_reset_timeout_uint32))
        
        try:
            status = _EApiStatus(status_value)
            if status != _EApiStatus.SUCCESS:
                return status, None, None, None
        except ValueError:
            print(f"Unknown EAPI status value : {status_value}")
            exit()
        
        max_delay_in_ms = max_delay_uint32.value
        max_event_timeout_in_ms = max_event_timeout_uint32.value
        max_reset_timeout_in_ms = max_reset_timeout_uint32.value
        return status, max_delay_in_ms, max_event_timeout_in_ms, max_reset_timeout_in_ms
    
    def watchdog_start(self, delay: int, event_timeout: int, reset_timeout: int) -> _EApiStatus:
        """
        Start watchdog timer.
        """
        
        delay_uint32 = c_uint32(delay)
        event_timeout_uint32 = c_uint32(event_timeout)
        reset_timeout_uint32 = c_uint32(reset_timeout)
        
        status_value: int = self.__EApiWDogStart(
            delay_uint32,
            event_timeout_uint32,
            reset_timeout_uint32)
        
        try:
            status = _EApiStatus(status_value)
        except ValueError:
            print(f"Unknown EAPI status value : {status_value}")
            exit()
        
        return status
    
    def watchdog_trigger(self) -> _EApiStatus:
        """
        Trigger watchdog timer.
        """
        
        status_value: int = self.__EApiWDogTrigger()
        
        try:
            status = _EApiStatus(status_value)
        except ValueError:
            print(f"Unknown EAPI status value : {status_value}")
            exit()
        
        return status
        
    def watchdog_stop(self) -> _EApiStatus:
        """
        Stop watchdog timer.
        """
        
        status_value: int = self.__EApiWDogStop()
        
        try:
            status = _EApiStatus(status_value)
        except ValueError:
            print(f"Unknown EAPI status value : {status_value}")
            exit()
        
        return status
    
    ################################################################
    
    # Feature : ETP
    
    def etp_read_device_data(self) -> Tuple[_EApiStatus, Union[_ETP_DATA, None]]:
        """
        Read device data from the ETP (Embedded Technology Platform).
        """
        
        device_data = pointer(pointer(_ETP_DATA()))
        # device_data = pointer(pointer(ETP_USER_DATA()))
        
        status_value = self.__EApiETPReadDeviceData(device_data)
        
        try:
            status = _EApiStatus(status_value)
            if status != _EApiStatus.SUCCESS:
                return status, None
        except ValueError:
            print(f"Unknown EAPI status value : {status_value}")
            exit()

        # argument 1: <class 'TypeError'>: expected LP_LP_ETP_USER_DATA instance instead of LP_LP_ETP_DATA
        etp_device_data = device_data.contents.contents
        device_order_text = bytes(etp_device_data.DeviceOrderText).decode('utf-8').strip('\x00')
        device_drder_number = bytes(etp_device_data.DeviceOrderNumber).decode('utf-8').strip('\x00')
        device_index = bytes(etp_device_data.DeviceIndex).decode('utf-8').strip('\x00')
        device_serial_umber = bytes(etp_device_data.DeviceSerialNumber).decode('utf-8').strip('\x00')
        device_operating_system = bytes(etp_device_data.OperatingSystem).decode('utf-8').strip('\x00')
        device_image = bytes(etp_device_data.Image).decode('utf-8').strip('\x00')
        reverse = bytes(etp_device_data.Reverse).decode('utf-8').strip('\x00')
        print("status ", status)
        print("device_order_text: ", device_order_text)
        print("device_drder_number: ", device_drder_number)
        print("DeviceIndex: ", device_index)
        print("DeviceSerialNumber: ", device_serial_umber)
        print("OperatingSystem: ", device_operating_system)
        print("Image: ", device_image)
        print("Reverse: ", reverse)

        return status, device_data
    
    def etp_read_user_data(self) -> Tuple[_EApiStatus, Union[_ETP_USER_DATA, None]]:
        """
        Read user data from the ETP (Embedded Technology Platform).
        """
        
        user_data = pointer(pointer(_ETP_USER_DATA()))
        
        status_value = self.__EApiETPReadUserData(user_data)
        
        try:
            status = _EApiStatus(status_value)
            if status != _EApiStatus.SUCCESS:
                return status, None
        except ValueError:
            print(f"Unknown EAPI status value : {status_value}")
            exit()

        etp_user_data = user_data.contents.contents
        userspace_1 = bytes(etp_user_data.UserSpace1).decode('utf-8').strip('\x00')
        userspace_2 = bytes(etp_user_data.UserSpace2).decode('utf-8').strip('\x00')
        print("status ", status)
        print("userspace1: ", userspace_1)
        print("userspace2: ", userspace_2)
        
        return status, user_data
    
    ################################################################
    
    # Feature : LED control

    def get_led_id_list(self) -> List[int]:
        return self.__led_id_list

    def get_led_status(self, id: _EApiId) -> Tuple[_EApiStatus, Union[int, None]]:
        """
        Get the status of an external function.
        """
        
        id_uint32 = c_uint32(id.value)
        funcStatus_uint32 = c_uint32()
        
        status_value: int = self.__EApiExtFunctionGetStatus(id_uint32, byref(funcStatus_uint32))
        
        try:
            status = _EApiStatus(status_value)
            if status != _EApiStatus.SUCCESS:
                return status, None
        except ValueError:
            print(f"Unknown EAPI status value : {status_value}")
            exit()
        
        funcStatus = funcStatus_uint32.value
        return status, funcStatus

    def set_led_status(self, id: _EApiId, funcStatus: int) -> _EApiStatus:
        """
        Set the status of an external function.
        """
        
        id_uint32 = c_uint32(id.value)
        funcStatus_uint32 = c_uint32(funcStatus)
        
        status_value = self.__EApiExtFunctionSetStatus(id_uint32, funcStatus_uint32)
        
        try:
            status = _EApiStatus(status_value)
        except ValueError:
            print(f"Unknown EAPI status value : {status_value}")
            exit()

        return status
    
################################################################

__EAPI_KELVINS_OFFSET = 2731

def EAPI_ENCODE_CELCIUS(celsius: float) -> float:
    return ((celsius) * 10) + __EAPI_KELVINS_OFFSET

def EAPI_DECODE_CELCIUS(kelvins: float) -> float:
    return ((kelvins) - __EAPI_KELVINS_OFFSET) / 10

def EAPI_DECODE_HWMON_VALUE(rawValue: float) -> float:
    return rawValue / 1000.0

def EAPI_CELCIUS_TO_FAHRENHEIT(celsius: float) -> float:
    return 32.0 + (celsius * 9.0 / 5.0)

################################################################

def EAPI_GPIO_GPIO_ID(GPIO_NUM: int) -> int:
    return GPIO_NUM

def EAPI_ID_GPIO_BANK(BANK_NUM: int) -> int:
    return _EApiId.EAPI_ID_GPIO_BANK_BASE.value | BANK_NUM
    
def EAPI_ID_GPIO_PIN_BANK(GPIO_NUM: int) -> int:
    return _EApiId.EAPI_ID_GPIO_BANK_BASE.value | (GPIO_NUM >> 5)

def EAPI_GPIO_PIN_BANK_MASK(GPIO_NUM: int) -> int:
    return 1 << (GPIO_NUM & 0x1F)
    
def EAPI_GPIO_PIN_BANK_TEST_STATE(GPIO_NUM: int , TState: int, TValue: int) -> bool:
    return ((TValue >> (GPIO_NUM & 0x1F)) & 1) == (TState)
    