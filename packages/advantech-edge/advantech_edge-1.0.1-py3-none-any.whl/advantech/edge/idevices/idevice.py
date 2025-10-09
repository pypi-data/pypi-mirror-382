from abc import ABC, abstractmethod

class IDevice(ABC):
    """
    Interface for all devices.
    This interface defines the basic properties and methods that all devices must implement.
    """
    
    @property
    @abstractmethod
    def description(self) -> str:
        """
        Description of the device.
        Returns:
            str: Description of the device.
        """
        pass