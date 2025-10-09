from abc import abstractmethod
from typing import Union

from .ifeature import IFeature

from ..dmi_info import DmiInfo

class IPlatformInformation(IFeature):
    """
    Interface for platform information.
    This interface provides methods to retrieve various platform-related information
    such as motherboard name, manufacturer, BIOS revision, driver version, library version,
    EC revision, and DMI information.
    """
    
    @property
    @abstractmethod
    def motherboard_name(self) -> str:
        """ 
        Get the motherboard name.
        Returns:
            str: Motherboard name
        """
        pass
    
    @property
    @abstractmethod
    def manufacturer(self) -> str:
        """
        Get the motherboard manufacturer.
        Returns:
            str: Motherboard manufacturer
        """
        pass

    @property
    @abstractmethod
    def bios_revision(self) -> str:
        """
        Get BIOS revision.
        Returns:
            str: BIOS revision
        """
        pass
    
    @property
    @abstractmethod
    def library_version(self) -> str:
        """
        Get the library version.
        Returns:
            str: Library version
        """
        pass
    
    @property
    @abstractmethod
    def driver_version(self) -> str:
        """
        Get the driver version.
        Returns:
            str: Driver version
        """
        pass
    
    @property
    @abstractmethod
    def ec_revision(self) -> str:
        """
        Get the EC (Embedded Controller) revision.
        Returns:
            str: EC (Embedded Controller) revision
        """
        pass
    
    @property
    @abstractmethod
    def dmi_info(self) -> Union[DmiInfo, None]:
        """
        Get the DMI information.
        Returns:
            DmiInfo: DMI information, None if not supported
        """
        pass
