from typing import Dict

from enum import Enum

from ..._internal._eapi._eapi_gpio import _EApiGpioDirectionType, _EApiGpioLevelType

from ...ifeatures.ionboardsensors import TemperatureSources
from ...ifeatures.ionboardsensors import VoltageSources
from ...ifeatures.ionboardsensors import FanSources
from ...ifeatures.ionboardsensors import CurrentSources
from ...ifeatures.ionboardsensors import PowerSources

from ...ifeatures.igpio import GpioDirectionTypes, GpioLevelTypes

class _EApiId(Enum):
    
    #
    #      C A P A B I L I T Y   V A L U E S
    #

    EAPI_ID_CAP_MAX = 12
    EAPI_ID_CAP_BASE = 0x00060000
    EAPI_ID_CAP_HWMON = EAPI_ID_CAP_BASE + 0
    EAPI_ID_CAP_HWMON_TEMPERATURE = EAPI_ID_CAP_BASE + 1
    EAPI_ID_CAP_HWMON_VOLTAGE = EAPI_ID_CAP_BASE + 2
    EAPI_ID_CAP_HWMON_FAN = EAPI_ID_CAP_BASE + 3
    EAPI_ID_CAP_HWMON_CURRENT = EAPI_ID_CAP_BASE + 4
    EAPI_ID_CAP_HWMON_POWER = EAPI_ID_CAP_BASE + 5
    EAPI_ID_CAP_GPIO = EAPI_ID_CAP_BASE + 6
    EAPI_ID_CAP_GPIO_COUNT = EAPI_ID_CAP_BASE + 7
    EAPI_ID_CAP_GPIO_INTERRUPT = EAPI_ID_CAP_BASE + 8
    EAPI_ID_CAP_BRIGHTNESS = EAPI_ID_CAP_BASE + 9
    EAPI_ID_CAP_WDOG = EAPI_ID_CAP_BASE + 10
    EAPI_ID_CAP_ETP = EAPI_ID_CAP_BASE + 11

    #
    #      B O A R D   V A L U E S
    #

    # IDS
    EAPI_ID_GET_NAME_MASK = 0xF0000000
    #EAPI_ID_GET_NAME_BASE(Id) = Id & EAPI_ID_GET_NAME_MASK

    EAPI_ID_BASE_GET_NAME_INFO = 0x00000000
    EAPI_ID_BASE_GET_NAME_HWMON = 0x10000000

    EAPI_ID_BOARD_MANUFACTURER_STR = 0x0
    EAPI_ID_BOARD_NAME_STR = 0x1
    EAPI_ID_BOARD_REVISION_STR = 0x2            # Board Version String
    EAPI_ID_BOARD_SERIAL_STR = 0x3              # Board Serial Number String
    EAPI_ID_BOARD_BIOS_REVISION_STR = 0x4
    EAPI_ID_BOARD_HW_REVISION_STR = 0x5         # Board Hardware Revision String
    EAPI_ID_BOARD_PLATFORM_TYPE_STR = 0x6       # Platform ID (ETX COM Express etc...)
    EAPI_ID_BOARD_EC_REVISION_STR = 0x101       # EC version
    EAPI_ID_BOARD_OS_REVISION_STR = 0x102       # OS version
    EAPI_ID_BOARD_CPU_MODEL_NAME_STR = 0x103    # CPU model name

    # DMI
    EAPI_ID_BOARD_DMIBIOS_VENDOR_STR = 0x201
    EAPI_ID_BOARD_DMIBIOS_VERSION_STR = 0x202
    EAPI_ID_BOARD_DMIBIOS_DATE_STR = 0x203
    EAPI_ID_BOARD_DMISYS_UUID_STR = 0x204
    EAPI_ID_BOARD_DMISYS_VENDOR_STR = 0x205
    EAPI_ID_BOARD_DMISYS_PRODUCT_STR = 0x206
    EAPI_ID_BOARD_DMISYS_VERSION_STR = 0x207
    EAPI_ID_BOARD_DMISYS_SERIAL_STR = 0x208
    EAPI_ID_BOARD_DMIBOARD_VENDOR_STR = 0x209
    EAPI_ID_BOARD_DMIBOARD_NAME_STR = 0x20a
    EAPI_ID_BOARD_DMIBOARD_VERSION_STR = 0x20b
    EAPI_ID_BOARD_DMIBOARD_SERIAL_STR = 0x20c
    EAPI_ID_BOARD_DMIBOARD_ASSET_TAG_STR = 0x20d

    #
    #      B O A R D   I N F O M A T I O N   V A L U E S
    #

    #EAPI_ID_GET_INDEX(Id) = Id & 0xFF
    #EAPI_ID_GET_TYPE(Id) = Id & 0x000FF000

    # IDS
    # We start from 0x00050000 to to avoid conflict => SUSI_ID + 0x00030000
    EAPI_ID_HWMON_TEMP_MAX = 10                                # Maximum temperature item number
    EAPI_ID_HWMON_TEMP_BASE = 0x00050000
    EAPI_ID_HWMON_TEMP = EAPI_ID_HWMON_TEMP_BASE
    EAPI_ID_HWMON_TEMP_CPU = EAPI_ID_HWMON_TEMP_BASE + 0       # 0.1 Kelvins
    EAPI_ID_HWMON_TEMP_CHIPSET = EAPI_ID_HWMON_TEMP_BASE + 1   # 0.1 Kelvins
    EAPI_ID_HWMON_TEMP_SYSTEM = EAPI_ID_HWMON_TEMP_BASE + 2    # 0.1 Kelvins
    EAPI_ID_HWMON_TEMP_CPU2 = EAPI_ID_HWMON_TEMP_BASE + 3      # 0.1 Kelvins
    EAPI_ID_HWMON_TEMP_OEM0 = EAPI_ID_HWMON_TEMP_BASE + 4      # 0.1 Kelvins
    EAPI_ID_HWMON_TEMP_OEM1 = EAPI_ID_HWMON_TEMP_BASE + 5      # 0.1 Kelvins
    EAPI_ID_HWMON_TEMP_OEM2 = EAPI_ID_HWMON_TEMP_BASE + 6      # 0.1 Kelvins
    EAPI_ID_HWMON_TEMP_OEM3 = EAPI_ID_HWMON_TEMP_BASE + 7      # 0.1 Kelvins
    EAPI_ID_HWMON_TEMP_OEM4 = EAPI_ID_HWMON_TEMP_BASE + 8      # 0.1 Kelvins
    EAPI_ID_HWMON_TEMP_OEM5 = EAPI_ID_HWMON_TEMP_BASE + 9      # 0.1 Kelvins

    EAPI_ID_HWMON_VOLTAGE_MAX = 24                                  # Maximum voltage item number
    EAPI_ID_HWMON_VOLTAGE_BASE = 0x00051000
    EAPI_ID_HWMON_VOLTAGE = EAPI_ID_HWMON_VOLTAGE_BASE
    EAPI_ID_HWMON_VOLTAGE_VCORE = EAPI_ID_HWMON_VOLTAGE_BASE + 0    # millivolts
    EAPI_ID_HWMON_VOLTAGE_VCORE2 = EAPI_ID_HWMON_VOLTAGE_BASE + 1   # millivolts
    EAPI_ID_HWMON_VOLTAGE_2V5 = EAPI_ID_HWMON_VOLTAGE_BASE + 2      # millivolts
    EAPI_ID_HWMON_VOLTAGE_3V3 = EAPI_ID_HWMON_VOLTAGE_BASE + 3      # millivolts
    EAPI_ID_HWMON_VOLTAGE_5V = EAPI_ID_HWMON_VOLTAGE_BASE + 4       # millivolts
    EAPI_ID_HWMON_VOLTAGE_12V = EAPI_ID_HWMON_VOLTAGE_BASE + 5      # millivolts
    EAPI_ID_HWMON_VOLTAGE_5VSB = EAPI_ID_HWMON_VOLTAGE_BASE + 6     # millivolts
    EAPI_ID_HWMON_VOLTAGE_3VSB = EAPI_ID_HWMON_VOLTAGE_BASE + 7     # millivolts
    EAPI_ID_HWMON_VOLTAGE_VBAT = EAPI_ID_HWMON_VOLTAGE_BASE + 8     # millivolts
    EAPI_ID_HWMON_VOLTAGE_5NV = EAPI_ID_HWMON_VOLTAGE_BASE + 9      # millivolts
    EAPI_ID_HWMON_VOLTAGE_12NV = EAPI_ID_HWMON_VOLTAGE_BASE + 10    # millivolts
    EAPI_ID_HWMON_VOLTAGE_VTT = EAPI_ID_HWMON_VOLTAGE_BASE + 11     # millivolts
    EAPI_ID_HWMON_VOLTAGE_24V = EAPI_ID_HWMON_VOLTAGE_BASE + 12     # millivolts
    EAPI_ID_HWMON_VOLTAGE_DC = EAPI_ID_HWMON_VOLTAGE_BASE + 13      # millivolts
    EAPI_ID_HWMON_VOLTAGE_DCSTBY = EAPI_ID_HWMON_VOLTAGE_BASE + 14  # millivolts
    EAPI_ID_HWMON_VOLTAGE_VBATLI = EAPI_ID_HWMON_VOLTAGE_BASE + 15  # millivolts
    EAPI_ID_HWMON_VOLTAGE_OEM0 = EAPI_ID_HWMON_VOLTAGE_BASE + 16    # millivolts
    EAPI_ID_HWMON_VOLTAGE_OEM1 = EAPI_ID_HWMON_VOLTAGE_BASE + 17    # millivolts
    EAPI_ID_HWMON_VOLTAGE_OEM2 = EAPI_ID_HWMON_VOLTAGE_BASE + 18    # millivolts
    EAPI_ID_HWMON_VOLTAGE_OEM3 = EAPI_ID_HWMON_VOLTAGE_BASE + 19    # millivolts
    EAPI_ID_HWMON_VOLTAGE_1V05 = EAPI_ID_HWMON_VOLTAGE_BASE + 20    # millivolts
    EAPI_ID_HWMON_VOLTAGE_1V5 = EAPI_ID_HWMON_VOLTAGE_BASE + 21     # millivolts
    EAPI_ID_HWMON_VOLTAGE_1V8 = EAPI_ID_HWMON_VOLTAGE_BASE + 22     # millivolts
    EAPI_ID_HWMON_VOLTAGE_DC2 = EAPI_ID_HWMON_VOLTAGE_BASE + 23     # millivolts

    EAPI_ID_HWMON_FAN_MAX = 10                                      # Maximum fan item number
    EAPI_ID_HWMON_FAN_BASE = 0x00052000
    EAPI_ID_HWMON_FAN_CPU = EAPI_ID_HWMON_FAN_BASE + 0              # RPM
    EAPI_ID_HWMON_FAN_SYSTEM = EAPI_ID_HWMON_FAN_BASE + 1           # RPM
    EAPI_ID_HWMON_FAN_CPU2 = EAPI_ID_HWMON_FAN_BASE + 2             # RPM
    EAPI_ID_HWMON_FAN_OEM0 = EAPI_ID_HWMON_FAN_BASE + 3             # RPM
    EAPI_ID_HWMON_FAN_OEM1 = EAPI_ID_HWMON_FAN_BASE + 4             # RPM
    EAPI_ID_HWMON_FAN_OEM2 = EAPI_ID_HWMON_FAN_BASE + 5             # RPM
    EAPI_ID_HWMON_FAN_OEM3 = EAPI_ID_HWMON_FAN_BASE + 6             # RPM
    EAPI_ID_HWMON_FAN_OEM4 = EAPI_ID_HWMON_FAN_BASE + 7             # RPM
    EAPI_ID_HWMON_FAN_OEM5 = EAPI_ID_HWMON_FAN_BASE + 8             # RPM
    EAPI_ID_HWMON_FAN_OEM6 = EAPI_ID_HWMON_FAN_BASE + 9             # RPM

    EAPI_ID_HWMON_CURRENT_MAX = 3                                   # Maximum current item number
    EAPI_ID_HWMON_CURRENT_BASE = 0x00053000
    EAPI_ID_HWMON_CURRENT_OEM0 = EAPI_ID_HWMON_CURRENT_BASE + 0     # milliampere
    EAPI_ID_HWMON_CURRENT_OEM1 = EAPI_ID_HWMON_CURRENT_BASE + 1     # milliampere
    EAPI_ID_HWMON_CURRENT_OEM2 = EAPI_ID_HWMON_CURRENT_BASE + 2     # milliampere

    EAPI_ID_HWMON_POWER_MAX = 1                                     # Maximum current item number
    EAPI_ID_HWMON_POWER_BASE = 0x00054000
    EAPI_ID_HWMON_POWER_OEM0 = EAPI_ID_HWMON_POWER_BASE + 0         # millwatt

    EAPI_ID_HWMON_MAX = EAPI_ID_HWMON_VOLTAGE_MAX                   # Maximum item number
    
    EAPI_ID_GPIO_POE_PINNUM = 0x00070001                            # Supported in Linux only

    #
    #      D I S P L A Y   V A L U E S ( EAPI VGA )
    #

    EAPI_ID_BACKLIGHT_MAX = 3
    EAPI_ID_BACKLIGHT_1 = 0
    EAPI_ID_BACKLIGHT_2 = 1
    EAPI_ID_BACKLIGHT_3 = 2

    EAPI_ID_DISPLAY_BRIGHTNESS_MAXIMUM = 0x00010000
    EAPI_ID_DISPLAY_BRIGHTNESS_MINIMUM = 0x00010001
    EAPI_ID_DISPLAY_AUTO_BRIGHTNESS = 0x00010002
    
    #
    #     E X T E N S I O N   F U N C T I O N S
    #
    
    EAPI_ID_EXT_FUNC_LED_MIN = 0x00000000
    EAPI_ID_EXT_FUNC_LED_MAX = 0x0000000F
    
    #------------------------------------------------------------------------------------------------------------
    #
    #
    #      G P I O
    #
    #
    #------------------------------------------------------------------------------------------------------------
    #
    #
    # +-----------------------------------------------+
    # |              Physical GPIO                    |
    # +-----+-----+-----+-----+-----+-----+-----+-----+
    # |  0  |  1  |  2  |  3  |  4  |  5  |  6  |  7  |
    # +-----+-----+-----+-----+-----+-----+-----+-----+
    #    |     |     |     |     |     |     |     |
    #    |     |     |     |     |     |     |     +-----------------------------------------------+
    #    |     |     |     |     |     |     |     |                                               |
    #    |     |     |     |     |     |     +-----|-----------------------------------------+     |
    #    |     |     |     |     |     |     |     |                                         |     |
    #    |     |     |     |     |     +-----|-----|-----------------------------------+     |     |
    #    |     |     |     |     |     |     |     |                                   |     |     |
    #    |     |     |     |     +-----|-----|-----|-----------------------------+     |     |     |
    #    |     |     |     |     |     |     |     |                             |     |     |     |
    #    |     |     |     +-----|-----|-----|-----|-----------------------+     |     |     |     |
    #    |     |     |     |     |     |     |     |                       |     |     |     |     |
    #    |     |     +-----|-----|-----|-----|-----|-----------------+     |     |     |     |     |
    #    |     |     |     |     |     |     |     |                 |     |     |     |     |     |
    #    |     +-----|-----|-----|-----|-----|-----|-----------+     |     |     |     |     |     |
    #    |     |     |     |     |     |     |     |           |     |     |     |     |     |     |
    #    +-----|-----|-----|-----|-----|-----|-----|-----+     |     |     |     |     |     |     |
    #    |     |     |     |     |     |     |     |     |     |     |     |     |     |     |     |
    #    |     |     |     |     |     |     |     |  +-----+-----+-----+-----+-----+-----+-----+-----+
    #    |     |     |     |     |     |     |     |  | Bit | Bit | Bit | Bit | Bit | Bit | Bit | Bit |
    #    |     |     |     |     |     |     |     |  |  0  |  1  |  2  |  3  |  4  |  5  |  6  |  7  |
    #    |     |     |     |     |     |     |     |  +-----------------------------------------------+
    #    |     |     |     |     |     |     |     |  |            EAPI_ID_GPIO_BITMASK00             |
    #    |     |     |     |     |     |     |     |  +-----------------------------------------------+
    #    |     |     |     |     |     |     |     |
    #    |     |     |     |     |     |     |     |     0     0     0     0     0     0     0
    #    |     |     |     |     |     |     |  +-----+-----+-----+-----+-----+-----+-----+-----+
    #    |     |     |     |     |     |     |  | Bit | Bit | Bit | Bit | Bit | Bit | Bit | Bit |
    #    |     |     |     |     |     |     |  |  0  |  1  |  2  |  3  |  4  |  5  |  6  |  7  |
    #    |     |     |     |     |     |     |  +-----------------------------------------------+
    #    |     |     |     |     |     |     |  |            EAPI_ID_GPIO_GPIO07                |
    #    |     |     |     |     |     |     |  +-----------------------------------------------+
    #    |     |     |     |     |     |     |
    #    |     |     |     |     |     |     |     0     0     0     0     0     0     0
    #    |     |     |     |     |     |  +-----+-----+-----+-----+-----+-----+-----+-----+
    #    |     |     |     |     |     |  | Bit | Bit | Bit | Bit | Bit | Bit | Bit | Bit |
    #    |     |     |     |     |     |  |  0  |  1  |  2  |  3  |  4  |  5  |  6  |  7  |
    #    |     |     |     |     |     |  +-----------------------------------------------+
    #    |     |     |     |     |     |  |            EAPI_ID_GPIO_GPIO06                |
    #    |     |     |     |     |     |  +-----------------------------------------------+
    #    |     |     |     |     |     |
    #    |     |     |     |     |     |     0     0     0     0     0     0     0
    #    |     |     |     |     |  +-----+-----+-----+-----+-----+-----+-----+-----+
    #    |     |     |     |     |  | Bit | Bit | Bit | Bit | Bit | Bit | Bit | Bit |
    #    |     |     |     |     |  |  0  |  1  |  2  |  3  |  4  |  5  |  6  |  7  |
    #    |     |     |     |     |  +-----------------------------------------------+
    #    |     |     |     |     |  |            EAPI_ID_GPIO_GPIO05                |
    #    |     |     |     |     |  +-----------------------------------------------+
    #    |     |     |     |     |
    #    |     |     |     |     |     0     0     0     0     0     0     0
    #    |     |     |     |  +-----+-----+-----+-----+-----+-----+-----+-----+
    #    |     |     |     |  | Bit | Bit | Bit | Bit | Bit | Bit | Bit | Bit |
    #    |     |     |     |  |  0  |  1  |  2  |  3  |  4  |  5  |  6  |  7  |
    #    |     |     |     |  +-----------------------------------------------+
    #    |     |     |     |  |            EAPI_ID_GPIO_GPIO04                |
    #    |     |     |     |  +-----------------------------------------------+
    #    |     |     |     |
    #    |     |     |     |     0     0     0     0     0     0     0
    #    |     |     |  +-----+-----+-----+-----+-----+-----+-----+-----+
    #    |     |     |  | Bit | Bit | Bit | Bit | Bit | Bit | Bit | Bit |
    #    |     |     |  |  0  |  1  |  2  |  3  |  4  |  5  |  6  |  7  |
    #    |     |     |  +-----------------------------------------------+
    #    |     |     |  |            EAPI_ID_GPIO_GPIO03                |
    #    |     |     |  +-----------------------------------------------+
    #    |     |     |
    #    |     |     |     0     0     0     0     0     0     0
    #    |     |  +-----+-----+-----+-----+-----+-----+-----+-----+
    #    |     |  | Bit | Bit | Bit | Bit | Bit | Bit | Bit | Bit |
    #    |     |  |  0  |  1  |  2  |  3  |  4  |  5  |  6  |  7  |
    #    |     |  +-----------------------------------------------+
    #    |     |  |            EAPI_ID_GPIO_GPIO02                |
    #    |     |  +-----------------------------------------------+
    #    |     |
    #    |     |     0     0     0     0     0     0     0
    #    |  +-----+-----+-----+-----+-----+-----+-----+-----+
    #    |  | Bit | Bit | Bit | Bit | Bit | Bit | Bit | Bit |
    #    |  |  0  |  1  |  2  |  3  |  4  |  5  |  6  |  7  |
    #    |  +-----------------------------------------------+
    #    |  |            EAPI_ID_GPIO_GPIO01                |
    #    |  +-----------------------------------------------+
    #    |
    #    |     0     0     0     0     0     0     0
    # +-----+-----+-----+-----+-----+-----+-----+-----+
    # | Bit | Bit | Bit | Bit | Bit | Bit | Bit | Bit |
    # |  0  |  1  |  2  |  3  |  4  |  5  |  6  |  7  |
    # +-----------------------------------------------+
    # |            EAPI_ID_GPIO_GPIO00                |
    # +-----------------------------------------------+
    #/
    #    /* IDs */
    #    /*
    # Individual ID Per GPIO Mapping
    #/
    
    EAPI_GPIO_GPIO_BITMASK = 1
    
    EAPI_ID_GPIO_GPIO00 = 0         # (Optional)
    EAPI_ID_GPIO_GPIO01 = 1         # (Optional)
    EAPI_ID_GPIO_GPIO02 = 2         # (Optional)
    EAPI_ID_GPIO_GPIO03 = 3         # (Optional)

    #
    # Multiple GPIOs Per ID Mapping
    #
    EAPI_ID_GPIO_BANK_BASE = 0x10000
    
    # EAPI_ID_GPIO_BANK00 = EAPI_ID_GPIO_BANK(0)     # GPIOs  0 - 31 (optional) 
    # EAPI_ID_GPIO_BANK01 = EAPI_ID_GPIO_BANK(1)     # GPIOs 32 - 63 (optional)
    # EAPI_ID_GPIO_BANK02 = EAPI_ID_GPIO_BANK(2)     # GPIOs 64 - 95 (optional)
    # EAPI_ID_GPIO_BANK03 = EAPI_ID_GPIO_BANK(3)     # GPIOs 96 - 127 (optional)

class _EApiIdUtilities:
    
    #################################################################################
    
    # ID name mapping.

    __displayNameDict: Dict[_EApiId, str] = {
        
        _EApiId.EAPI_ID_BOARD_MANUFACTURER_STR: "Board manufacturer",
        _EApiId.EAPI_ID_BOARD_NAME_STR: "Board name",
        _EApiId.EAPI_ID_BOARD_BIOS_REVISION_STR: "BIOS revision",
        _EApiId.EAPI_ID_BOARD_EC_REVISION_STR: "EC revision",

        _EApiId.EAPI_ID_BOARD_DMIBIOS_VENDOR_STR: "DMI BIOS vendor",
        _EApiId.EAPI_ID_BOARD_DMIBIOS_VERSION_STR: "DMI BIOS version",
        _EApiId.EAPI_ID_BOARD_DMIBIOS_DATE_STR: "DMI BIOS date",
        _EApiId.EAPI_ID_BOARD_DMISYS_UUID_STR: "DMI system UUID",
        _EApiId.EAPI_ID_BOARD_DMISYS_VENDOR_STR: "DMI system vendor",
        _EApiId.EAPI_ID_BOARD_DMISYS_PRODUCT_STR: "DMI system product",
        _EApiId.EAPI_ID_BOARD_DMISYS_VERSION_STR: "DMI system version",
        _EApiId.EAPI_ID_BOARD_DMISYS_SERIAL_STR: "DMI system serial",
        _EApiId.EAPI_ID_BOARD_DMIBOARD_VENDOR_STR: "DMI board vendor",
        _EApiId.EAPI_ID_BOARD_DMIBOARD_NAME_STR: "DMI board name",
        _EApiId.EAPI_ID_BOARD_DMIBOARD_VERSION_STR: "DMI board version",
        _EApiId.EAPI_ID_BOARD_DMIBOARD_SERIAL_STR: "DMI board serial",
        _EApiId.EAPI_ID_BOARD_DMIBOARD_ASSET_TAG_STR: "DMI board asset tag",

        _EApiId.EAPI_ID_HWMON_TEMP_CPU: "CPU",
        _EApiId.EAPI_ID_HWMON_TEMP_CHIPSET: "Chipset",
        _EApiId.EAPI_ID_HWMON_TEMP_SYSTEM: "System",
        _EApiId.EAPI_ID_HWMON_TEMP_CPU2: "CPU2",
        _EApiId.EAPI_ID_HWMON_TEMP_OEM0: "OEM0",
        _EApiId.EAPI_ID_HWMON_TEMP_OEM1: "OEM1",
        _EApiId.EAPI_ID_HWMON_TEMP_OEM2: "OEM2",
        _EApiId.EAPI_ID_HWMON_TEMP_OEM3: "OEM3",
        _EApiId.EAPI_ID_HWMON_TEMP_OEM4: "OEM4",
        _EApiId.EAPI_ID_HWMON_TEMP_OEM5: "OEM5",

        _EApiId.EAPI_ID_HWMON_VOLTAGE_VCORE: "Core",
        _EApiId.EAPI_ID_HWMON_VOLTAGE_VCORE2: "Core",
        _EApiId.EAPI_ID_HWMON_VOLTAGE_2V5: "2.5V",
        _EApiId.EAPI_ID_HWMON_VOLTAGE_3V3: "3.3V",
        _EApiId.EAPI_ID_HWMON_VOLTAGE_5V: "5V",
        _EApiId.EAPI_ID_HWMON_VOLTAGE_12V: "12V",
        _EApiId.EAPI_ID_HWMON_VOLTAGE_5VSB: "Standy 5V",
        _EApiId.EAPI_ID_HWMON_VOLTAGE_3VSB: "Standy 3V",
        _EApiId.EAPI_ID_HWMON_VOLTAGE_VBAT: "Battery",
        _EApiId.EAPI_ID_HWMON_VOLTAGE_5NV: "-5V",
        _EApiId.EAPI_ID_HWMON_VOLTAGE_12NV: "-12V",
        _EApiId.EAPI_ID_HWMON_VOLTAGE_VTT: "DIMM",
        _EApiId.EAPI_ID_HWMON_VOLTAGE_24V: "24V",
        _EApiId.EAPI_ID_HWMON_VOLTAGE_DC: "DC",
        _EApiId.EAPI_ID_HWMON_VOLTAGE_DCSTBY: "Standy DC",
        _EApiId.EAPI_ID_HWMON_VOLTAGE_VBATLI: "Li-ion Battery",
        _EApiId.EAPI_ID_HWMON_VOLTAGE_OEM0: "OEM0",
        _EApiId.EAPI_ID_HWMON_VOLTAGE_OEM1: "OEM1",
        _EApiId.EAPI_ID_HWMON_VOLTAGE_OEM2: "OEM2",
        _EApiId.EAPI_ID_HWMON_VOLTAGE_OEM3: "OEM3",
        _EApiId.EAPI_ID_HWMON_VOLTAGE_1V05: "1.05V",
        _EApiId.EAPI_ID_HWMON_VOLTAGE_1V5: "1.5V",
        _EApiId.EAPI_ID_HWMON_VOLTAGE_1V8: "1.8V",
        _EApiId.EAPI_ID_HWMON_VOLTAGE_DC2: "DC2",

        _EApiId.EAPI_ID_HWMON_FAN_CPU: "CPU",
        _EApiId.EAPI_ID_HWMON_FAN_SYSTEM: "System",
        _EApiId.EAPI_ID_HWMON_FAN_CPU2: "CPU2",
        _EApiId.EAPI_ID_HWMON_FAN_OEM0: "OEM0",
        _EApiId.EAPI_ID_HWMON_FAN_OEM1: "OEM1",
        _EApiId.EAPI_ID_HWMON_FAN_OEM2: "OEM2",
        _EApiId.EAPI_ID_HWMON_FAN_OEM3: "OEM3",
        _EApiId.EAPI_ID_HWMON_FAN_OEM4: "OEM4",
        _EApiId.EAPI_ID_HWMON_FAN_OEM5: "OEM5",
        _EApiId.EAPI_ID_HWMON_FAN_OEM6: "OEM6",

        _EApiId.EAPI_ID_HWMON_CURRENT_OEM0: "OEM0",
        _EApiId.EAPI_ID_HWMON_CURRENT_OEM1: "OEM1",
        _EApiId.EAPI_ID_HWMON_CURRENT_OEM2: "OEM2",

        _EApiId.EAPI_ID_HWMON_POWER_OEM0: "OEM0"
    }

    @classmethod
    def eapi_id_to_display_name(cls, id: _EApiId) -> str:
        
        if id in cls.__displayNameDict:
            return cls.__displayNameDict[id]
        raise KeyError(f"No display name mapping defined for {id}")

    #################################################################################

    # Enum mapping : Temperature Sources

    __temperature_src_to_eapi_id_dict: Dict[TemperatureSources, _EApiId] = {
        TemperatureSources.Cpu: _EApiId.EAPI_ID_HWMON_TEMP_CPU,
        TemperatureSources.Cpu2: _EApiId.EAPI_ID_HWMON_TEMP_CPU2,
        TemperatureSources.System: _EApiId.EAPI_ID_HWMON_TEMP_SYSTEM,
        TemperatureSources.Chipset: _EApiId.EAPI_ID_HWMON_TEMP_CHIPSET
    }
    
    @classmethod
    def temperature_sources_to_eapi_id(cls, src: TemperatureSources) -> _EApiId:
        
        if src in cls.__temperature_src_to_eapi_id_dict:
            return cls.__temperature_src_to_eapi_id_dict[src]
        raise KeyError(f"No temperature source mapping defined for {src}")
    
    @classmethod
    def eapi_id_to_temperature_source(cls, id: _EApiId) -> TemperatureSources:
    
        for key, value in cls.__temperature_src_to_eapi_id_dict.items():
            if value == id:
                return key
        raise KeyError(f"No temperature source mapping defined for {id}") 

    #################################################################################

    # Enum mapping : Voltage Sources

    __voltage_src_to_eapi_id_dict: Dict[VoltageSources, _EApiId] = {
        VoltageSources.Core: _EApiId.EAPI_ID_HWMON_VOLTAGE_VCORE,
        VoltageSources.Core2: _EApiId.EAPI_ID_HWMON_VOLTAGE_VCORE2,
        VoltageSources.Battery: _EApiId.EAPI_ID_HWMON_VOLTAGE_VBAT,
        VoltageSources.Bus2P5V: _EApiId.EAPI_ID_HWMON_VOLTAGE_2V5,
        VoltageSources.Bus3P3V: _EApiId.EAPI_ID_HWMON_VOLTAGE_3V3,
        VoltageSources.Bus5V: _EApiId.EAPI_ID_HWMON_VOLTAGE_5V,
        VoltageSources.Bus12V: _EApiId.EAPI_ID_HWMON_VOLTAGE_12V,
        VoltageSources.Bus24V: _EApiId.EAPI_ID_HWMON_VOLTAGE_24V,
        VoltageSources.BusMinus5V: _EApiId.EAPI_ID_HWMON_VOLTAGE_5NV,
        VoltageSources.BusMinus12V: _EApiId.EAPI_ID_HWMON_VOLTAGE_12NV
    }
    
    @classmethod
    def voltage_sources_to_eapi_id(cls, src: VoltageSources) -> _EApiId:
        
        if src in cls.__voltage_src_to_eapi_id_dict:
            return cls.__voltage_src_to_eapi_id_dict[src]
        raise KeyError(f"No voltage source mapping defined for {src}")
    
    @classmethod
    def eapi_id_to_voltage_source(cls, id: _EApiId) -> VoltageSources:
        
        for key, value in cls.__voltage_src_to_eapi_id_dict.items():
            if value == id:
                return key
        raise KeyError(f"No voltage source mapping defined for {id}")

    #################################################################################

    # Enum mapping : Fan Sources
    
    __fan_src_to_eapi_id_dict: Dict[FanSources, _EApiId] = {
        FanSources.Cpu: _EApiId.EAPI_ID_HWMON_FAN_CPU,
        FanSources.Cpu2: _EApiId.EAPI_ID_HWMON_FAN_CPU2,
        FanSources.System: _EApiId.EAPI_ID_HWMON_FAN_SYSTEM
    }
    
    @classmethod
    def fan_sources_to_eapi_id(cls, src: FanSources) -> _EApiId:
        
        if src in cls.__fan_src_to_eapi_id_dict:
            return cls.__fan_src_to_eapi_id_dict[src]
        raise KeyError(f"No fan speed source mapping defined for {src}")
    
    @classmethod
    def eapi_id_to_fan_source(cls, id: _EApiId) -> FanSources:
        
        for key, value in cls.__fan_src_to_eapi_id_dict.items():
            if value == id:
                return key
        raise KeyError(f"No fan speed measure point id mapping defined for {id}")

    #################################################################################

    # Enum mapping : Current Sources
    
    __current_src_to_eapi_id_dict : Dict[CurrentSources, _EApiId] = {
    }
    
    @classmethod
    def current_sources_to_eapi_id(cls, src: CurrentSources) -> _EApiId:
        
        if src in cls.__current_src_to_eapi_id_dict:
            return cls.__current_src_to_eapi_id_dict[src]
        raise KeyError(f"No current source mapping defined for {src}")
    
    @classmethod
    def eapi_id_to_current_sources(cls, id: _EApiId) -> CurrentSources:
        
        for key, value in cls.__current_src_to_eapi_id_dict.items():
            if value == id:
                return key
        raise KeyError(f"No current measure point id mapping defined for {id}")

    #################################################################################

    # Enum mapping : Power Sources

    __power_src_to_eapi_id_dict: Dict[PowerSources, _EApiId] = {
    }
    
    @classmethod
    def power_sources_to_eapi_id(cls, src: PowerSources) -> _EApiId:
        
        if src in cls.__power_src_to_eapi_id_dict:
            return cls.__power_src_to_eapi_id_dict[src]
        raise KeyError(f"No power source mapping defined for {src}")

    @classmethod
    def eapi_id_to_power_sources(cls, id: _EApiId) -> PowerSources:
        
        for key, value in cls.__power_src_to_eapi_id_dict.items():
            if value == id:
                return key
        raise KeyError(f"No power measure point id mapping defined for {id}")

    #################################################################################

    # Enum mapping : GPIO

    __gpio_direction_types_to_eapi_gpio_direction_type_dict = {
        GpioDirectionTypes.Input: _EApiGpioDirectionType.EAPI_GPIO_INPUT,
        GpioDirectionTypes.Output: _EApiGpioDirectionType.EAPI_GPIO_OUTPUT
    }

    __gpio_level_types_to_eapi_gpio_level_type_dict = {
        GpioLevelTypes.Low: _EApiGpioLevelType.EAPI_GPIO_LOW,
        GpioLevelTypes.High: _EApiGpioLevelType.EAPI_GPIO_HIGH
    }
    
    @classmethod
    def gpio_direction_types_to_eapi_gpio_direction_type(cls, type: GpioDirectionTypes) -> _EApiGpioDirectionType:
        
        if type in cls.__gpio_direction_types_to_eapi_gpio_direction_type_dict:
            return cls.__gpio_direction_types_to_eapi_gpio_direction_type_dict[type]
        raise KeyError(f"No GPIO direction type mapping defined for {type}")
    
    @classmethod
    def eapi_gpio_direction_type_to_gpio_direction_types(cls, type: _EApiGpioDirectionType) -> GpioDirectionTypes:
        
        for key, value in cls.__gpio_direction_types_to_eapi_gpio_direction_type_dict.items():
            if value == type:
                return key
        raise KeyError(f"No GPIO direction type mapping defined for {type}")
    
    @classmethod
    def gpio_level_types_to_eapi_gpio_level_type(cls, type: GpioLevelTypes) -> _EApiGpioLevelType:
        
        if type in cls.__gpio_level_types_to_eapi_gpio_level_type_dict:
            return cls.__gpio_level_types_to_eapi_gpio_level_type_dict[type]
        raise KeyError(f"No GPIO level type mapping defined for {type}")
    
    @classmethod
    def eapi_gpio_level_type_to_gpio_level_types(cls, type: _EApiGpioLevelType) -> GpioLevelTypes:
        
        for key, value in cls.__gpio_level_types_to_eapi_gpio_level_type_dict.items():
            if value == type:
                return key
        raise KeyError(f"No GPIO level type mapping defined for {type}")