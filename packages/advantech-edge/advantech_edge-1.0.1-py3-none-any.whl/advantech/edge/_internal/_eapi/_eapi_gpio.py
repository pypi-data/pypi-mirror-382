from enum import Enum
    
class _EApiGpioBitMaskStates(Enum):
    
    # Bit mask Bit States
    EAPI_GPIO_BITMASK_SELECT = 1
    EAPI_GPIO_BITMASK_NOSELECT = 0
    
class _EApiGpioDirectionType(Enum):
    
    EAPI_GPIO_OUTPUT = 0
    EAPI_GPIO_INPUT = 1

class _EApiGpioLevelType(Enum):
    
    EAPI_GPIO_LOW = 0
    EAPI_GPIO_HIGH = 1