from abc import ABC, abstractmethod

class IFeature(ABC):
    """
    Interface for a feature.
    """
    
    @property
    @abstractmethod
    def is_supported(self) -> bool:
        """
        Returns True if the feature is supported, False otherwise.
        Returns:
            bool: True if the feature is supported, False otherwise.
        """
        pass