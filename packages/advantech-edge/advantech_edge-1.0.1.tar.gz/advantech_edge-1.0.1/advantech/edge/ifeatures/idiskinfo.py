from abc import abstractmethod

from typing import Union
from typing import List

from .ifeature import IFeature

class IDiskInfo(IFeature):
    """
    Interface for disk information.
    This interface provides methods to retrieve information about the disk space.
    """
    
    @property
    @abstractmethod
    def disks(self) -> List[str]:
        """
        List of disks
        Returns:
            List[str]: List of disks
        """
        pass
    
    @abstractmethod
    def get_total_space(self, disk: Union[str, int]) -> Union[int, None]:
        """
        Get the total space of specified disk in bytes.
        Returns:
            int: Total space of specified disk in bytes.
        """
        pass
    
    @abstractmethod
    def get_free_space(self, disk: Union[str, int]) -> Union[int, None]:
        """
        Get the free space of specified disk in bytes.
        Returns:
            int: Free space of specified disk in bytes.
        """
        pass
