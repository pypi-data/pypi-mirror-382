import threading
from typing import Union
from typing import List

from .._internal._feature_provider._feature_provider import _FeatureProvider

from ..ifeatures.iwatchdog import IWatchdog

class Watchdog(IWatchdog):
    
    ################################################################

    __instance = None 
    __lock = threading.Lock()
    
    def __new__(cls):
        with cls.__lock:
            if not cls.__instance:
                cls.__instance = super(Watchdog, cls).__new__(cls)
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
        return self.__provider.is_watchdog_supported
    
    ################################################################
    
    @property
    def timers(self) -> List[str]:
        return self.__provider.watchdog_timers
    
    def start_timer(self, timer: Union[str, int], delay: int, event_timeout: int, reset_timeout: int) -> None:
        self.__provider.watchdog_start_timer(timer, delay, event_timeout, reset_timeout)
    
    def stop_timer(self, timer: Union[str, int]) -> None:
        self.__provider.watchdog_stop_timer(timer)
    
    def trigger_timer(self, timer: Union[str, int]) -> None:
        self.__provider.watchdog_trigger_timer(timer)