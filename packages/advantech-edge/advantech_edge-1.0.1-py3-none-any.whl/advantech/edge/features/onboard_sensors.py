import threading
from typing import List
from typing import Union

from .._internal._feature_provider._feature_provider import _FeatureProvider

from ..ifeatures.ionboardsensors import IOnboardSensors
from ..ifeatures.ionboardsensors import TemperatureSources
from ..ifeatures.ionboardsensors import VoltageSources
from ..ifeatures.ionboardsensors import FanSources

class OnboardSensors(IOnboardSensors):
    
    ################################################################

    __instance = None
    __lock = threading.Lock()

    def __new__(cls):
        with cls.__lock:
            if not cls.__instance:
                cls.__instance = super(OnboardSensors, cls).__new__(cls)
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
        return self.__provider.is_onboard_sensors_supported

    ################################################################

    @property
    def temperature_sources(self) -> List[str]:
        return self.__provider.onboard_sensors_temperature_sources

    def get_temperature(self, src: Union[str, TemperatureSources]) -> Union[float, None]:
        return self.__provider.onboard_sensors_get_temperature(src)

    @property
    def voltage_sources(self) -> List[str]:
        return self.__provider.onboard_sensors_voltage_sources

    def get_voltage(self, src: Union[str, VoltageSources]) -> Union[float, None]:
        return self.__provider.onboard_sensors_get_voltage(src)
    
    @property
    def fan_sources(self) -> List[str]:
        return self.__provider.onboard_sensors_fan_sources
    
    def get_fan_speed(self, src: Union[str, FanSources]) -> Union[float, None]:
        return self.__provider.onboard_sensors_get_fan_speed(src)