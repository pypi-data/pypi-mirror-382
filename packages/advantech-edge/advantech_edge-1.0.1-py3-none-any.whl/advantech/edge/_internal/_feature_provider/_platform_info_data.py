from typing import Union

from ...dmi_info import DmiInfo

class _PlatformInfoData:
    """
    This class is used to store platform information data.
    """
    def __init__(self,
                 motherboard_name: str,
                 manufacturer: str,
                 boot_up_times: Union[int, None],
                 running_time_in_hours: Union[float, None],
                 bios_revision: Union[str, None],
                 firmware_name: Union[str, None],
                 firmware_version: Union[str, None],
                 library_version: Union[str, None],
                 driver_version: Union[str, None],
                 ec_revision: Union[str, None],
                 dmi_info: Union[DmiInfo, None]):
        self.__motherboard_name = motherboard_name
        self.__manufacturer = manufacturer
        self.__boot_up_times = boot_up_times
        self.__running_time_in_hours = running_time_in_hours
        self.__bios_revision = bios_revision
        self.__firmware_name = firmware_name
        self.__firmware_version = firmware_version
        self.__library_version = library_version
        self.__driver_version = driver_version
        self.__ec_revision = ec_revision
        self.__dmi_info = dmi_info
        
    @property
    def motherboard_name(self) -> str:
        return self.__motherboard_name
        
    @property
    def manufacturer(self) -> str:
        return self.__manufacturer
    
    @property
    def boot_up_times(self) -> Union[int, None]:
        return self.__boot_up_times
    
    @property
    def running_time_in_hours(self) -> Union[float, None]:
        return self.__running_time_in_hours
    
    @property
    def bios_revision(self) -> Union[str, None]:
        return self.__bios_revision
    
    @property
    def firmware_name(self) -> Union[str, None]:
        return self.__firmware_name
            
    @property
    def firmware_version(self) -> Union[str, None]:
        return self.__firmware_version
    
    @property
    def library_version(self) -> Union[str, None]:
        return self.__library_version
    
    @property
    def driver_version(self) -> Union[str, None]:
        return self.__driver_version
    
    @property
    def ec_revision(self) -> Union[str, None]:
        return self.__ec_revision
    
    @property
    def dmi_info(self) -> Union[DmiInfo, None]:
        return self.__dmi_info