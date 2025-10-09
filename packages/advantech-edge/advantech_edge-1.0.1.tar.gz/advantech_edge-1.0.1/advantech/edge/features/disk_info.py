import threading

from typing import Union
from typing import List

from ..ifeatures.idiskinfo import IDiskInfo

from .._internal._feature_provider._feature_provider import _FeatureProvider

class DiskInfo(IDiskInfo):

    ################################################################

    __instance = None
    __lock = threading.Lock()
    
    def __new__(cls):
        with cls.__lock:
            if not cls.__instance:
                cls.__instance = super(DiskInfo, cls).__new__(cls)
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
        return self.__provider.is_disk_info_supported
    
    ################################################################
    
    @property
    def disks(self) -> List[str]:
        return self.__provider.disk_info_disks
    
    def get_total_space(self, disk: Union[str, int]) -> Union[int, None]:
        return self.__provider.disk_info_get_total_space(disk)
    
    def get_free_space(self, disk: Union[str, int]) -> Union[int, None]:
        return self.__provider.disk_info_get_free_space(disk)