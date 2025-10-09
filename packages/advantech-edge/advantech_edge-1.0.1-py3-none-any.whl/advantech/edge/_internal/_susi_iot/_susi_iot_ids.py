from typing import Dict
from typing import NamedTuple
from enum import IntEnum

from ._susi_iot_gpio import _SusiIotGpioDirectionType, _SusiIotGpioLevelType

from ...ifeatures.ionboardsensors import TemperatureSources
from ...ifeatures.ionboardsensors import VoltageSources
from ...ifeatures.ionboardsensors import FanSources
from ...ifeatures.ionboardsensors import CurrentSources
from ...ifeatures.ionboardsensors import PowerSources

from ...ifeatures.igpio import GpioDirectionTypes, GpioLevelTypes

class _SusiIotId(IntEnum):

    SusiIotVersion = 257
    
    PlatformInformation = 65536
    
    BootUpTimes = 16843010
    RunningTimeInHours = 16843011
    
    BoardManufacturer = 16843777
    BoardName = 16843778
    
    FirmwareVersion = 16843267
    
    BiosRevision = 16843781
    FirmwareName = 16843784
    
    DriverVersion = 16843265
    LibraryVersion = 16843266

    HardwareMonitor = 131072
    HardwareMonitorTemperature = 131328
    HardwareMonitorTemperatureCpu = 16908545
    HardwareMonitorTemperatureCpu2 = 16908546
    HardwareMonitorTemperatureSystem = 16908547
    
    HardwareMonitorTemperatureGpu = 16908549
    
    HardwareMonitorVoltage = 131584
    HardwareMonitorVoltageCore = 16908801
    HardwareMonitorVoltage3P3V = 16908804
    HardwareMonitorVoltage5V = 16908805
    HardwareMonitorVoltage12V = 16908806
    HardwareMonitorVoltageStandby5V = 16908807
    HardwareMonitorVoltageCmosBattery = 16908809
    HardwareMonitorVoltageDcPower = 16908814
    HardwareMonitorVoltageVcc3V = 16908817
    HardwareMonitorFanSpeed = 131840
    HardwareMonitorFanSpeedCpu = 16909057
    HardwareMonitorFanSpeedSys1 = 16909058
    HardwareMonitorFanSpeedSys2 = 16909060

    Gpio = 262144
    Gpio00 = 17039617
    GpioDir00 = 17039873
    GpioLevel00 = 17040129
    Gpio01 = 17039618
    GpioDir01 = 17039874
    GpioLevel01 = 17040130
    Gpio02 = 17039619
    GpioDir02 = 17039875
    GpioLevel02 = 17040131
    Gpio03 = 17039620
    GpioDir03 = 17039876
    GpioLevel03 = 17040132
    Gpio04 = 17039621
    GpioDir04 = 17039877
    GpioLevel04 = 17040133
    Gpio05 = 17039622
    GpioDir05 = 17039878
    GpioLevel05 = 17040134
    Gpio06 = 17039623
    GpioDir06 = 17039879
    GpioLevel06 = 17040135
    Gpio07 = 17039624
    GpioDir07 = 17039880
    GpioLevel07 = 17040136
    Gpio08 = 17039625
    GpioDir08 = 17039881
    GpioLevel08 = 17040137
    Gpio09 = 17039626
    GpioDir09 = 17039882
    GpioLevel09 = 17040138
    Gpio10 = 17039627
    GpioDir10 = 17039883
    GpioLevel10 = 17040139
    Gpio11 = 17039628
    GpioDir11 = 17039884
    GpioLevel11 = 17040140
    Gpio12 = 17039629
    GpioDir12 = 17039885
    GpioLevel12 = 17040141
    Gpio13 = 17039630
    GpioDir13 = 17039886
    GpioLevel13 = 17040142
    Gpio14 = 17039631
    GpioDir14 = 17039887
    GpioLevel14 = 17040143
    Gpio15 = 17039632
    GpioDir15 = 17039888
    GpioLevel15 = 17040144
    Gpio16 = 17039633
    GpioDir16 = 17039889
    GpioLevel16 = 17040145
    Gpio17 = 17039634
    GpioDir17 = 17039890
    GpioLevel17 = 17040146
    Gpio18 = 17039635
    GpioDir18 = 17039891
    GpioLevel18 = 17040147
    Gpio19 = 17039636
    GpioDir19 = 17039892
    GpioLevel19 = 17040148
    Gpio20 = 17039637
    GpioDir20 = 17039893
    GpioLevel20 = 17040149
    
    Sdram0 = 337117185
    SdramMemoryType0 = 337117441
    SdramMemoryModuleType0 = 337117697
    SdramMemorySizeInGigaBytes0 = 337117953
    SdramMemorySpeed0 = 337118209
    SdramMemoryRank0 = 337118465
    SdramMemoryVoltage0 = 337118721
    SdramMemoryBank0 = 337118977
    SdramMemoryManufacturingDateCode0 = 337119233
    SdramMemoryTemperature0 = 337119489
    SdramMemoryWriteProtection0 = 337119745
    SdramMemoryModuleManufacture0 = 337120001 
    SdramMemoryManufacture0 = 337120257
    SdramMemoryPartNumber0 = 337121537
    SdramMemorySpecific0 = 337125633
    
    DiskInfoTotalDiskSpace = 353697792
    DiskInfoFreeDiskSpace = 353697793

class _SusiIotGpioIdTuple(NamedTuple):
    pin_id: _SusiIotId
    dir_id: _SusiIotId
    level_id: _SusiIotId

class _SusiIotIdUtilities:
    
    #################################################################################

    __susi_iot_base_name_dict: Dict[_SusiIotId, str] = {
        
        _SusiIotId.PlatformInformation: "Platform Information",
        _SusiIotId.BoardManufacturer: "Board manufacturer",
        _SusiIotId.BoardName: "Board name",
        _SusiIotId.BiosRevision: "BIOS revision",
        _SusiIotId.DriverVersion: "Driver version",
        _SusiIotId.LibraryVersion: "Library version",

        _SusiIotId.HardwareMonitor: "Hardware Monitor",
        _SusiIotId.HardwareMonitorTemperature: "Hardware Monitor Temperature",
        _SusiIotId.HardwareMonitorTemperatureCpu: "Hardware Monitor Temperature CPU",
        _SusiIotId.HardwareMonitorTemperatureCpu2: "Hardware Monitor Temperature CPU2",
        _SusiIotId.HardwareMonitorTemperatureSystem: "Hardware Monitor Temperature System",
        _SusiIotId.HardwareMonitorTemperatureGpu: "Hardware Monitor Temperature GPU",
        _SusiIotId.HardwareMonitorVoltage: "Hardware Monitor Voltage",
        _SusiIotId.HardwareMonitorVoltageCore: "Hardware Monitor Voltage Vcore",
        _SusiIotId.HardwareMonitorVoltage3P3V: "Hardware Monitor Voltage 3.3V",
        _SusiIotId.HardwareMonitorVoltage5V: "Hardware Monitor Voltage 5V",
        _SusiIotId.HardwareMonitorVoltage12V: "Hardware Monitor Voltage 12V",
        _SusiIotId.HardwareMonitorVoltageStandby5V: "Hardware Monitor Voltage 5V Standby",
        _SusiIotId.HardwareMonitorVoltageCmosBattery: "Hardware Monitor Voltage CMOS Battery",
        _SusiIotId.HardwareMonitorVoltageVcc3V: "Hardware Monitor Voltage VCC3V",
        _SusiIotId.HardwareMonitorFanSpeed: "Hardware Monitor Fan Speed",
        _SusiIotId.HardwareMonitorFanSpeedCpu: "Hardware Monitor Fan Speed CPU",
        _SusiIotId.HardwareMonitorFanSpeedSys1: "Hardware Monitor Fan Speed Sys1",
        _SusiIotId.HardwareMonitorFanSpeedSys2: "Hardware Monitor Fan Speed Sys2",

        _SusiIotId.Gpio: "GPIO",
        _SusiIotId.Gpio00: "GPIO 00",
        _SusiIotId.GpioDir00: "GPIO 00 Dir",
        _SusiIotId.GpioLevel00: "GPIO 00 Level",
        _SusiIotId.Gpio01: "GPIO 01",
        _SusiIotId.GpioDir01: "GPIO 01 Dir",
        _SusiIotId.GpioLevel01: "GPIO 01 Level",
        _SusiIotId.Gpio02: "GPIO 02",
        _SusiIotId.GpioDir02: "GPIO 02 Dir",
        _SusiIotId.GpioLevel02: "GPIO 02 Level",
        _SusiIotId.Gpio03: "GPIO 03",
        _SusiIotId.GpioDir03: "GPIO 03 Dir",
        _SusiIotId.GpioLevel03: "GPIO 03 Level",
        _SusiIotId.Gpio04: "GPIO 04",
        _SusiIotId.GpioDir04: "GPIO 04 Dir",
        _SusiIotId.GpioLevel04: "GPIO 04 Level",
        _SusiIotId.Gpio05: "GPIO 05",
        _SusiIotId.GpioDir05: "GPIO 05 Dir",
        _SusiIotId.GpioLevel05: "GPIO 05 Level",
        _SusiIotId.Gpio06: "GPIO 06",
        _SusiIotId.GpioDir06: "GPIO 06 Dir",
        _SusiIotId.GpioLevel06: "GPIO 06 Level",
        _SusiIotId.Gpio07: "GPIO 07",
        _SusiIotId.GpioDir07: "GPIO 07 Dir",
        _SusiIotId.GpioLevel07: "GPIO 07 Level",
        _SusiIotId.Gpio08: "GPIO 08",
        _SusiIotId.GpioDir08: "GPIO 08 Dir",
        _SusiIotId.GpioLevel08: "GPIO 08 Level",
        _SusiIotId.Gpio09: "GPIO 09",
        _SusiIotId.GpioDir09: "GPIO 09 Dir",
        _SusiIotId.GpioLevel09: "GPIO 09 Level",
        _SusiIotId.Gpio10: "GPIO 10",
        _SusiIotId.GpioDir10: "GPIO 10 Dir",
        _SusiIotId.GpioLevel10: "GPIO 10 Level",
        _SusiIotId.Gpio11: "GPIO 11",
        _SusiIotId.GpioDir11: "GPIO 11 Dir",
        _SusiIotId.GpioLevel11: "GPIO 11 Level",
        _SusiIotId.Gpio12: "GPIO 12",
        _SusiIotId.GpioDir12: "GPIO 12 Dir",
        _SusiIotId.GpioLevel12: "GPIO 12 Level",
        _SusiIotId.Gpio13: "GPIO 13",
        _SusiIotId.GpioDir13: "GPIO 13 Dir",
        _SusiIotId.GpioLevel13: "GPIO 13 Level",
        _SusiIotId.Gpio14: "GPIO 14",
        _SusiIotId.GpioDir14: "GPIO 14 Dir",
        _SusiIotId.GpioLevel14: "GPIO 14 Level",
        _SusiIotId.Gpio15: "GPIO 15",
        _SusiIotId.GpioDir15: "GPIO 15 Dir",
        _SusiIotId.GpioLevel15: "GPIO 15 Level",
        _SusiIotId.Gpio16: "GPIO 16",
        _SusiIotId.GpioDir16: "GPIO 16 Dir",
        _SusiIotId.GpioLevel16: "GPIO 16 Level",
        _SusiIotId.Gpio17: "GPIO 17",
        _SusiIotId.GpioDir17: "GPIO 17 Dir",
        _SusiIotId.GpioLevel17: "GPIO 17 Level",
        _SusiIotId.Gpio18: "GPIO 18",
        _SusiIotId.GpioDir18: "GPIO 18 Dir",
        _SusiIotId.GpioLevel18: "GPIO 18 Level",
        _SusiIotId.Gpio19: "GPIO 19",
        _SusiIotId.GpioDir19: "GPIO 19 Dir",
        _SusiIotId.GpioLevel19: "GPIO 19 Level",
        _SusiIotId.Gpio20: "GPIO 20",
        _SusiIotId.GpioDir20: "GPIO 20 Dir",
        _SusiIotId.GpioLevel20: "GPIO 20 Level"
    }
    
    @classmethod
    def susi_iot_id_to_display_name(cls, id: _SusiIotId) -> str:
        
        if id in cls.__susi_iot_base_name_dict:
            return cls.__susi_iot_base_name_dict[id]
        raise KeyError(f"Fail to get display name of {id}")
    
    #################################################################################

    # Enum mapping : Temperature Sources

    __temperature_src_to_susi_iot_id_dict: Dict[TemperatureSources, _SusiIotId] = {
        TemperatureSources.Cpu: _SusiIotId.HardwareMonitorTemperatureCpu,
        TemperatureSources.Cpu2: _SusiIotId.HardwareMonitorTemperatureCpu2,
        TemperatureSources.System: _SusiIotId.HardwareMonitorTemperatureSystem,
        TemperatureSources.Gpu: _SusiIotId.HardwareMonitorTemperatureGpu
    }
    
    @classmethod
    def temperature_sources_to_susi_iot_id(cls, src: TemperatureSources) -> _SusiIotId:
        
        if src in cls.__temperature_src_to_susi_iot_id_dict:
            return cls.__temperature_src_to_susi_iot_id_dict[src]
        raise KeyError(f"No temperature source mapping defined for {src}")

    @classmethod
    def susi_iot_id_to_temperature_sources(cls, id: _SusiIotId) -> TemperatureSources:
        
        for key, value in cls.__temperature_src_to_susi_iot_id_dict.items():
            if value == id:
                return key
        raise KeyError(f"No temperature source mapping defined for {id}")
    
    #################################################################################
    
    # Enum mapping : Voltage Sources
    
    __voltage_src_to_susi_iot_id_dict: Dict[VoltageSources, _SusiIotId] = {
        VoltageSources.Core: _SusiIotId.HardwareMonitorVoltageCore,
        VoltageSources.Bus3P3V: _SusiIotId.HardwareMonitorVoltage3P3V,
        VoltageSources.Bus5V: _SusiIotId.HardwareMonitorVoltage5V,
        VoltageSources.Bus12V: _SusiIotId.HardwareMonitorVoltage12V,
        VoltageSources.Battery: _SusiIotId.HardwareMonitorVoltageCmosBattery
    }
    
    @classmethod
    def voltage_sources_to_susi_iot_id(cls, src: VoltageSources) -> _SusiIotId:
        
        if src in cls.__voltage_src_to_susi_iot_id_dict:
            return cls.__voltage_src_to_susi_iot_id_dict[src]
        raise KeyError(f"No voltage source mapping defined for {src}")
    
    @classmethod
    def susi_iot_id_to_voltage_sources(cls, id: _SusiIotId) -> VoltageSources:
        
        for key, value in cls.__voltage_src_to_susi_iot_id_dict.items():
            if value == id:
                return key
        raise KeyError(f"No voltage source mapping defined for {id}")
    
    #################################################################################
    
    # Enum mapping : Fan Sources
    
    __fan_src_to_susi_iot_id_dict: Dict[FanSources, _SusiIotId] = {
        FanSources.Cpu: _SusiIotId.HardwareMonitorFanSpeedCpu,
        FanSources.System: _SusiIotId.HardwareMonitorFanSpeedSys1
    }
    
    @classmethod
    def fan_sources_to_susi_iot_id(cls, src: FanSources) -> _SusiIotId:
        
        if src in cls.__fan_src_to_susi_iot_id_dict:
            return cls.__fan_src_to_susi_iot_id_dict[src]
        raise KeyError(f"No fan speed source mapping defined for {src}")
    
    @classmethod
    def susi_iot_id_to_fan_sources(cls, id: _SusiIotId) -> FanSources:
        
        for key, value in cls.__fan_src_to_susi_iot_id_dict.items():
            if value == id:
                return key
        raise KeyError(f"No fan speed source mapping defined for {id}")
    
    #################################################################################
    
    # Enum mapping : Current Sources
    
    __current_src_to_susi_iot_id_dict: Dict[CurrentSources, _SusiIotId] = { 
    }
    
    @classmethod
    def current_sources_to_susi_iot_id(cls, src: CurrentSources) -> _SusiIotId:
        
        if src in cls.__current_src_to_susi_iot_id_dict:
            return cls.__current_src_to_susi_iot_id_dict[src]
        raise KeyError(f"No current source mapping defined for {src}")
    
    @classmethod
    def susi_iot_id_to_current_sources(cls, id: _SusiIotId) -> CurrentSources:
        
        for key, value in cls.__current_src_to_susi_iot_id_dict.items():
            if value == id:
                return key
        raise KeyError(f"No current measure point mapping defined for {id}")
    
    #################################################################################
    
    # Enum mapping : Power Sources
    
    __power_src_to_susi_iot_id_dict: Dict[PowerSources, _SusiIotId] = { 
    }
    
    @classmethod
    def power_sources_to_susi_iot_id(cls, src: PowerSources) -> _SusiIotId:
        
        if src in cls.__power_src_to_susi_iot_id_dict:
            return cls.__power_src_to_susi_iot_id_dict[src]
        raise KeyError(f"No power source mapping defined for {src}")
    
    @classmethod
    def susi_iot_id_to_power_sources(cls, id: _SusiIotId) -> PowerSources:
        
        for key, value in cls.__power_src_to_susi_iot_id_dict.items():
            if value == id:
                return key
        raise KeyError(f"No power measure point id mapping defined for {id}")

    #################################################################################

    # Dictionaries : GPIO

    __gpio_pin_no_to_susi_iot_id_tuple_dict: Dict[int, _SusiIotGpioIdTuple] = {
        0: _SusiIotGpioIdTuple(_SusiIotId.Gpio00, _SusiIotId.GpioDir00, _SusiIotId.GpioLevel00),
        1: _SusiIotGpioIdTuple(_SusiIotId.Gpio01, _SusiIotId.GpioDir01, _SusiIotId.GpioLevel01),
        2: _SusiIotGpioIdTuple(_SusiIotId.Gpio02, _SusiIotId.GpioDir02, _SusiIotId.GpioLevel02),
        3: _SusiIotGpioIdTuple(_SusiIotId.Gpio03, _SusiIotId.GpioDir03, _SusiIotId.GpioLevel03),
        4: _SusiIotGpioIdTuple(_SusiIotId.Gpio04, _SusiIotId.GpioDir04, _SusiIotId.GpioLevel04),
        5: _SusiIotGpioIdTuple(_SusiIotId.Gpio05, _SusiIotId.GpioDir05, _SusiIotId.GpioLevel05),
        6: _SusiIotGpioIdTuple(_SusiIotId.Gpio06, _SusiIotId.GpioDir06, _SusiIotId.GpioLevel06),
        7: _SusiIotGpioIdTuple(_SusiIotId.Gpio07, _SusiIotId.GpioDir07, _SusiIotId.GpioLevel07),
        8: _SusiIotGpioIdTuple(_SusiIotId.Gpio08, _SusiIotId.GpioDir08, _SusiIotId.GpioLevel08),
        9: _SusiIotGpioIdTuple(_SusiIotId.Gpio09, _SusiIotId.GpioDir09, _SusiIotId.GpioLevel09),
        10: _SusiIotGpioIdTuple(_SusiIotId.Gpio10, _SusiIotId.GpioDir10, _SusiIotId.GpioLevel10),
        11: _SusiIotGpioIdTuple(_SusiIotId.Gpio11, _SusiIotId.GpioDir11, _SusiIotId.GpioLevel11),
        12: _SusiIotGpioIdTuple(_SusiIotId.Gpio12, _SusiIotId.GpioDir12, _SusiIotId.GpioLevel12),
        13: _SusiIotGpioIdTuple(_SusiIotId.Gpio13, _SusiIotId.GpioDir13, _SusiIotId.GpioLevel13),
        14: _SusiIotGpioIdTuple(_SusiIotId.Gpio14, _SusiIotId.GpioDir14, _SusiIotId.GpioLevel14),
        15: _SusiIotGpioIdTuple(_SusiIotId.Gpio15, _SusiIotId.GpioDir15, _SusiIotId.GpioLevel15),
        16: _SusiIotGpioIdTuple(_SusiIotId.Gpio16, _SusiIotId.GpioDir16, _SusiIotId.GpioLevel16),
        17: _SusiIotGpioIdTuple(_SusiIotId.Gpio17, _SusiIotId.GpioDir17, _SusiIotId.GpioLevel17),
        18: _SusiIotGpioIdTuple(_SusiIotId.Gpio18, _SusiIotId.GpioDir18, _SusiIotId.GpioLevel18),
        19: _SusiIotGpioIdTuple(_SusiIotId.Gpio19, _SusiIotId.GpioDir19, _SusiIotId.GpioLevel19),
        20: _SusiIotGpioIdTuple(_SusiIotId.Gpio20, _SusiIotId.GpioDir20, _SusiIotId.GpioLevel20)
    }
    
    __gpio_direction_types_to_susi_iot_gpio_direction_types_dict: Dict[GpioDirectionTypes, _SusiIotGpioDirectionType] = {
        GpioDirectionTypes.Input: _SusiIotGpioDirectionType.INPUT,
        GpioDirectionTypes.Output: _SusiIotGpioDirectionType.OUTPUT
    }

    __gpio_level_types_to_susi_iot_gpio_level_types_dic: Dict[GpioLevelTypes, _SusiIotGpioLevelType] = {
        GpioLevelTypes.Low: _SusiIotGpioLevelType.LOW,
        GpioLevelTypes.High: _SusiIotGpioLevelType.HIGH
    }
    
    @classmethod
    def gpio_pin_index_to_susi_iot_id_tuple(cls, pin_index: int) -> _SusiIotGpioIdTuple:

        if pin_index in cls.__gpio_pin_no_to_susi_iot_id_tuple_dict:
            return cls.__gpio_pin_no_to_susi_iot_id_tuple_dict[pin_index]
        raise KeyError(f"No GPIO ID tuple mapping defined for pin number {pin_index}")
    
    @classmethod
    def gpio_pin_id_to_gpio_id_tuple(cls, pin_id: _SusiIotId) -> _SusiIotGpioIdTuple:

        for key, value in cls.__gpio_pin_no_to_susi_iot_id_tuple_dict.items():
            if value.pin_id == pin_id:
                return value
        raise KeyError(f"No GPIO ID tuple mapping defined for pin number {pin_id}")
    
    @classmethod
    def gpio_check_dir_id_in_susi_iot_id_tuple(cls, dir_id: _SusiIotId) -> bool:
        
        for key, value in cls.__gpio_pin_no_to_susi_iot_id_tuple_dict.items():
            if value.dir_id == dir_id:
                return True
        return False
    
    @classmethod
    def gpio_check_level_id_in_susi_iot_id_tuple(cls, level_id: _SusiIotId) -> bool:
        
        for key, value in cls.__gpio_pin_no_to_susi_iot_id_tuple_dict.items():
            if value.level_id == level_id:
                return True
        return False
    
    @classmethod
    def gpio_direction_types_to_susi_iot_gpio_direction_type(cls, type: GpioDirectionTypes) -> _SusiIotGpioDirectionType:
        
        if type in cls.__gpio_direction_types_to_susi_iot_gpio_direction_types_dict:
            return cls.__gpio_direction_types_to_susi_iot_gpio_direction_types_dict[type]
        raise KeyError(f"No GPIO direction type mapping defined for {type}")

    @classmethod
    def susi_iot_gpio_direction_type_to_gpio_direction_types(cls, type: _SusiIotGpioDirectionType) -> GpioDirectionTypes:
        
        for key, value in cls.__gpio_direction_types_to_susi_iot_gpio_direction_types_dict.items():
            if value == type:
                return key
        raise KeyError(f"No GPIO direction type mapping defined for {type}")
    
    @classmethod
    def gpio_level_types_to_susi_iot_gpio_level_type(cls, type: GpioLevelTypes) -> _SusiIotGpioLevelType:
        
        if type in cls.__gpio_level_types_to_susi_iot_gpio_level_types_dic:
            return cls.__gpio_level_types_to_susi_iot_gpio_level_types_dic[type]
        raise KeyError(f"No GPIO level type mapping defined for {type}")
    
    @classmethod
    def susi_iot_gpio_level_type_to_gpio_level_types(cls, type: _SusiIotGpioLevelType) -> GpioLevelTypes:
        
        for key, value in cls.__gpio_level_types_to_susi_iot_gpio_level_types_dic.items():
            if value == type:
                return key
        raise KeyError(f"No GPIO level type mapping defined for {type}")
    
    #################################################################################