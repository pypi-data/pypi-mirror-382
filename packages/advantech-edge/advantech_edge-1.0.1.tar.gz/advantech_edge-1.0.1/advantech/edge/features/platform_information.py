import threading
from typing import Union

from ..ifeatures import IPlatformInformation

from .._internal._feature_provider._feature_provider import _FeatureProvider
from .._internal._feature_provider._platform_info_data import _PlatformInfoData

from ..dmi_info import DmiInfo

class PlatformInformation(IPlatformInformation):

    ################################################################

    __instance = None 
    __lock = threading.Lock()
    
    def __new__(cls):
        with cls.__lock:
            if not cls.__instance:
                cls.__instance = super(PlatformInformation, cls).__new__(cls)
            return cls.__instance

    def __init__(self):

        # Check if the class is already initialized
        if not hasattr(self, '_initialized'):

            # Initialize the flag
            self._initialized = True

            # Initialize feature provider instance
            self.__provider = _FeatureProvider()
            self.__is_supported = self.__provider.is_platform_information_supported
            self.__platform_info_data = self.__provider.platform_info_data
        
    ################################################################
    
    @property
    def is_supported(self) -> bool:
        return self.__is_supported
    
    ################################################################

    @property
    def motherboard_name(self) -> str:
        return self.__platform_info_data.motherboard_name
    
    @property
    def manufacturer(self) -> str:
        return self.__platform_info_data.manufacturer

    @property
    def bios_revision(self) -> str:
        return self.__platform_info_data.bios_revision if self.__platform_info_data.bios_revision != None else str()
    
    @property
    def library_version(self) -> str:
        return self.__platform_info_data.library_version if self.__platform_info_data.library_version != None else str()
    
    @property
    def driver_version(self) -> str:
        return self.__platform_info_data.driver_version if self.__platform_info_data.driver_version != None else str()
    
    @property
    def ec_revision(self) -> str:
        return self.__platform_info_data.ec_revision if self.__platform_info_data.ec_revision != None else str()
    
    @property
    def dmi_info(self) -> Union[DmiInfo, None]:
        return self.__platform_info_data.dmi_info