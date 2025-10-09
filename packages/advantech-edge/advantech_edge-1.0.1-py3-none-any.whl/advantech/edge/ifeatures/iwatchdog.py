from abc import abstractmethod
from enum import Enum
from typing import List
from typing import Union

from .ifeature import IFeature

class WatchdogEventTypes(Enum):
    """
    Enum for Watchdog Event Types
    """
    
    EventTimeout = 0
    """
    Event Timeout
    """
    
class IWatchdog(IFeature):
    """
    Interface for Watchdog Feature
    """
    
    @property
    @abstractmethod
    def timers(self) -> List[str]:
        """
        List of watchdog timer
        Returns:
            List[str]: List of watchdog timer
        """
        pass
    
    @abstractmethod
    def start_timer(self, timer: Union[str, int], delay: int, event_timeout: int, reset_timeout: int) -> None:
        """
        Start the timer with the specified delay and timeouts.
        Args:
            timer (str | int): Timer name or index.
            delay (int): The delay in seconds before the timer expires.
            event_timeout (int): The timeout for the event in seconds.
            reset_timeout (int): The timeout for resetting the timer in seconds.
        """
        pass

    @abstractmethod
    def stop_timer(self, timer: Union[str, int]) -> None:
        """
        Stop the timer.
        Args:
            timer (str | int): Timer name or index.
        """
        pass

    @abstractmethod
    def trigger_timer(self, timer: Union[str, int]) -> None:
        """
        Trigger the timer.
        Args:
            timer (str | int): Timer name or index.
        """
        pass