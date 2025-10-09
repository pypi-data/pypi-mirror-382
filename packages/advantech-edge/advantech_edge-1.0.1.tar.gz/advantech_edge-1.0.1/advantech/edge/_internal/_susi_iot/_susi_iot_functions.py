import threading
import sys
import os
import platform
from typing import Union

import json

from ctypes import RTLD_GLOBAL
from ctypes import CDLL
from ctypes import c_int
from ctypes import c_size_t
from ctypes import c_char_p
from ctypes import Structure
from ctypes import POINTER
from ctypes import CFUNCTYPE

from ._susi_iot_status import _SusiIotStatus
from ._susi_iot_ids import _SusiIotId

class JsonType:
    JSON_OBJECT = 0
    JSON_ARRAY = 1
    JSON_STRING = 2
    JSON_INTEGER = 3
    JSON_REAL = 4
    JSON_TRUE = 5
    JSON_FALSE = 6
    JSON_NULL = 7

class JsonT(Structure):
    _fields_ = [
        ("type", c_int),
        ("refcount", c_size_t)
    ]

class _SusiIotFunctions:

    ################################################################

    __arch = platform.machine().lower()
    __os_name = platform.system()
    __path_susi_iot_lib = ""
    __path_json_lib = ""
    
    @classmethod
    def __lib_path_init(cls):
        
        try:

            # Get class members
            arch = cls.__arch
            os_name = cls.__os_name

            # Set library paths according to OS and architecture 
            if os_name == "Linux" and 'x86' in arch:
                cls.__path_susi_iot_lib = "/usr/lib/libSusiIoT.so"
                cls.__path_json_lib = "/usr/lib/libjansson.so"
            elif os_name == "Linux" and 'aarch64' in arch:
                cls.__path_susi_iot_lib = "/usr/lib/libSusiIoT.so"
                cls.__path_json_lib = "/usr/lib/libjansson.so"
            elif os_name == "Windows" and 'x86' in arch:
                raise NotImplementedError(f"Not implemented for {os_name} {arch}.")
            elif os_name == "Windows" and 'aarch64' in arch:
                raise NotImplementedError(f"Not implemented for {os_name} {arch}.")
            else:
                raise NotImplementedError(f"Not implemented for {os_name} {arch}.")

            # Check if library files exist.
            if not os.path.exists(cls.__path_susi_iot_lib):
                raise ModuleNotFoundError(path = cls.__path_susi_iot_lib)
            if not os.path.exists(cls.__path_json_lib):
                raise ModuleNotFoundError(path = cls.__path_json_lib)
            
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

    def __load_susi_iot_lib(self):

        #
        self.__lib_susi_iot = CDLL(self.__class__.__path_susi_iot_lib, mode = RTLD_GLOBAL)

        #
        ftype_SusiIoTInitialize = CFUNCTYPE(
            c_int
        )
        self.__SusiIoTInitialize = ftype_SusiIoTInitialize(("SusiIoTInitialize", self.__lib_susi_iot))

        ftype_SusiIoTUninitialize = CFUNCTYPE(
            c_int
        )
        self.__SusiIoTUninitialize = ftype_SusiIoTUninitialize(("SusiIoTUninitialize", self.__lib_susi_iot))

        ftype_SusiIoTGetPFCapabilityString = CFUNCTYPE(
            c_char_p
        )
        self.__SusiIoTGetPFCapabilityString = ftype_SusiIoTGetPFCapabilityString(("SusiIoTGetPFCapabilityString", self.__lib_susi_iot))
        
        ftype_SusiIoTGetPFDataString = CFUNCTYPE(
            c_char_p,
            c_int
        )
        self.__SusiIoTGetPFDataString = ftype_SusiIoTGetPFDataString(("SusiIoTGetPFDataString", self.__lib_susi_iot))

        ftype_SusiIoTGetPFDataStringByUri = CFUNCTYPE(
            c_char_p,
            c_char_p
        )
        self.__SusiIoTGetPFDataStringByUri = ftype_SusiIoTGetPFDataStringByUri(("SusiIoTGetPFDataStringByUri", self.__lib_susi_iot))

        ftype_SusiIoTSetValue = CFUNCTYPE(
            c_int,
            c_int,
            POINTER(JsonT)
        )
        self.__SusiIoTSetValue = ftype_SusiIoTSetValue(("SusiIoTSetValue", self.__lib_susi_iot))

        ftype_SusiIoTGetLoggerPath = CFUNCTYPE(
            c_char_p
        )
        self.__SusiIoTGetLoggerPath = ftype_SusiIoTGetLoggerPath(("SusiIoTGetLoggerPath", self.__lib_susi_iot))

    def __load_json_lib(self):

        #
        self.__lib_json = CDLL(self.__class__.__path_json_lib, mode=RTLD_GLOBAL)

        # 
        ftype_json_dumps = CFUNCTYPE(
            c_char_p
        )
        self.__json_dumps = ftype_json_dumps(("json_dumps", self.__lib_json))

        ftype_json_integer = CFUNCTYPE(
            POINTER(JsonT)
        )
        self.__json_integer = ftype_json_integer(("json_integer", self.__lib_json))

        ftype_json_real = CFUNCTYPE(
            POINTER(JsonT)
        )
        self.__json_real = ftype_json_real(("json_real", self.__lib_json))

        ftype_json_string = CFUNCTYPE(
            POINTER(JsonT)
        )
        self.__json_string = ftype_json_string(("json_string", self.__lib_json))

    ################################################################

    __instance = None
    __lock = threading.Lock()
    
    def __new__(cls):

        # Initialize library information
        cls.__lib_path_init()

        # Create instance
        with cls.__lock:
            if not cls.__instance:
                cls.__instance = super(_SusiIotFunctions, cls).__new__(cls)
            return cls.__instance

    def __init__(self):

        # Check if the class is already initialized
        if not hasattr(self, '_initialized'):

            # Initialize the flag
            self._initialized = True

            # Load libraries
            self.__load_susi_iot_lib()
            self.__load_json_lib()

            # Call SUSI IoT function : Initialize 
            status_value: int = self.__SusiIoTInitialize()
            try:
                status = _SusiIotStatus(status_value)
                if status != _SusiIotStatus.SUCCESS:
                    print(f"SUSI IoT initialization fail. Status : {status}")
                    exit()
            except ValueError:
                print(f"SUSI IoT initialization fail. Status value : {status_value}")
                exit()

    def __del__(self):

        # Check if the class is already initialized
        if self.__class__.__instance is not None:

            # Call SUSI IoT function : Uninitialize
            status_value: int = self.__SusiIoTUninitialize()
            try:
                status = _SusiIotStatus(status_value)
                if status != _SusiIotStatus.SUCCESS:
                    print(f"SUSI IoT uninitialization fail. Status : {status}")
                    exit()
            except ValueError:
                print(f"SUSI IoT uninitialization fail. Status value : {status_value}")
                exit()

            # # Set instance to None
            self.__class__.__instance = None

    ################################################################
    
    def __get_json_indent(self, n):
        json_max_indent = 0x1F
        return n & json_max_indent

    def __get_json_real_precision(self, n):
        return ((n & 0x1F) << 11)

    ################################################################

    def get_capability_string(self) -> str:
        cap_string: bytes = self.__SusiIoTGetPFCapabilityString()
        return cap_string.decode('utf-8')

    def get_data_by_id(self, id: _SusiIotId) -> dict:
        
        id_value_uint32 = c_int(id.value)
        
        data_str: bytes = self.__SusiIoTGetPFDataString(id_value_uint32)
        
        data_str_utf8 = data_str.decode('utf-8')
        json_obj = json.loads(data_str_utf8)
        
        return json_obj

    def set_value(self, id: _SusiIotId, value) -> None:
        
        result_ptr = self.__json_integer(value)
        
        result = result_ptr.contents
        
        self.__SusiIoTSetValue(id.value, result)