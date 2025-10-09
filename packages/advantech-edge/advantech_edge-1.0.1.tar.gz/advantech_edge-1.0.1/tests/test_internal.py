# from advantech.edge._internal._susi_iot._susi_iot import _SusiIot
# from advantech.edge._internal._susi_iot._susi_iot_gpio import SusiIotGpioDirectionTypes, SusiIotGpioLevelTypes

# print(SusiIotGpioDirectionTypes(0))

# _susi_iot = _SusiIot()
# for pin in _susi_iot.pins:
#     dir = _susi_iot.get_direction(pin)
#     level = _susi_iot.get_level(pin)
#     print(f"{pin}, direction : {dir}, level : {level}")

##############################################################

# from advantech.edge._internal._eapi._eapi_functions import _EApiId

# id_dict = {id.name: id.value for id in _EApiId}
# print(id_dict)

###################################################################


# from advantech.edge._internal._susi_iot._susi_iot_dicts import __temperature_src_to_susi_iot_id_dict

# for key, value in __temperature_src_to_susi_iot_id_dict.items():
#     print(f"{key}, {value}")

###################################################################

# from advantech.edge._internal._eapi._eapi_ids import _EApiId
# from advantech.edge._internal._eapi._eapi_status import _EApiStatus
# from advantech.edge._internal._eapi._eapi_functions import _EApiFunctions

# funcs = _EApiFunctions()

# # Read board info
# print(f"Board info strings :")
# status, board_info_str = funcs.board_info_get_string(_EApiId.EAPI_ID_BOARD_NAME_STR)
# motherboard_name = board_info_str if status == _EApiStatus.SUCCESS else str()
# print(f"- status : {status}, motherboard_name: {motherboard_name}")
# status, board_info_str = funcs.board_info_get_string(_EApiId.EAPI_ID_BOARD_MANUFACTURER_STR)
# manufacturer = board_info_str if status == _EApiStatus.SUCCESS else str()
# print(f"- status : {status}, manufacturer : {manufacturer}")
# status, board_info_str = funcs.board_info_get_string(_EApiId.EAPI_ID_BOARD_REVISION_STR)
# revision = board_info_str if status == _EApiStatus.SUCCESS else str()
# print(f"- status : {status}, revision : {revision}")
# status, board_info_str = funcs.board_info_get_string(_EApiId.EAPI_ID_BOARD_SERIAL_STR)
# serial = board_info_str if status == _EApiStatus.SUCCESS else str()
# print(f"- status : {status}, serial : {serial}")
# status, board_info_str = funcs.board_info_get_string(_EApiId.EAPI_ID_BOARD_BIOS_REVISION_STR)
# bios_revision = board_info_str if status == _EApiStatus.SUCCESS else str()
# print(f"- status : {status}, bios_revision : {bios_revision}")
# status, board_info_str = funcs.board_info_get_string(_EApiId.EAPI_ID_BOARD_HW_REVISION_STR)
# hw_revision = board_info_str if status == _EApiStatus.SUCCESS else str()
# print(f"- status : {status}, hw_revision : {hw_revision}")
# status, board_info_str = funcs.board_info_get_string(_EApiId.EAPI_ID_BOARD_PLATFORM_TYPE_STR)
# platform_type = board_info_str if status == _EApiStatus.SUCCESS else str()
# print(f"- status : {status}, platform_type : {platform_type}")
# status, board_info_str = funcs.board_info_get_string(_EApiId.EAPI_ID_BOARD_EC_REVISION_STR)
# ec_revision = board_info_str if status == _EApiStatus.SUCCESS else str()
# print(f"- status : {status}, ec_revision : {ec_revision}")
# status, board_info_str = funcs.board_info_get_string(_EApiId.EAPI_ID_BOARD_OS_REVISION_STR)
# os_revision = board_info_str if status == _EApiStatus.SUCCESS else str()
# print(f"- status : {status}, os_revision : {os_revision}")
# status, board_info_str = funcs.board_info_get_string(_EApiId.EAPI_ID_BOARD_CPU_MODEL_NAME_STR)
# cpu_model_name = board_info_str if status == _EApiStatus.SUCCESS else str()
# print(f"- status : {status}, cpu_model_name : {cpu_model_name}")

# # Read info : DMI
# status, board_info_str = funcs.board_info_get_string(_EApiId.EAPI_ID_BOARD_DMIBIOS_VENDOR_STR)
# dmi_info_bios_vendor = board_info_str if status == _EApiStatus.SUCCESS else str()
# print(f"- status : {status}, dmi_info_bios_vendor: {dmi_info_bios_vendor}")
# status, board_info_str = funcs.board_info_get_string(_EApiId.EAPI_ID_BOARD_DMIBIOS_VERSION_STR)
# dmi_info_bios_version = board_info_str if status == _EApiStatus.SUCCESS else str()
# print(f"- status : {status}, dmi_info_bios_version: {dmi_info_bios_version}")
# status, board_info_str = funcs.board_info_get_string(_EApiId.EAPI_ID_BOARD_DMIBIOS_DATE_STR)
# dmi_info_bios_release_date = board_info_str if status == _EApiStatus.SUCCESS else str()
# print(f"- status : {status}, dmi_info_bios_release_date: {dmi_info_bios_release_date}")
# status, board_info_str = funcs.board_info_get_string(_EApiId.EAPI_ID_BOARD_DMISYS_UUID_STR)
# dmi_info_sys_uuid = board_info_str if status == _EApiStatus.SUCCESS else str()
# print(f"- status : {status}, dmi_info_sys_uuid: {dmi_info_sys_uuid}")
# status, board_info_str = funcs.board_info_get_string(_EApiId.EAPI_ID_BOARD_DMISYS_VENDOR_STR)
# dmi_info_sys_vendor = board_info_str if status == _EApiStatus.SUCCESS else str()
# print(f"- status : {status}, dmi_info_sys_vendor: {dmi_info_sys_vendor}")
# status, board_info_str = funcs.board_info_get_string(_EApiId.EAPI_ID_BOARD_DMISYS_PRODUCT_STR)
# dmi_info_sys_product = board_info_str if status == _EApiStatus.SUCCESS else str()
# print(f"- status : {status}, dmi_info_sys_product: {dmi_info_sys_product}")
# status, board_info_str = funcs.board_info_get_string(_EApiId.EAPI_ID_BOARD_DMISYS_VERSION_STR)
# dmi_info_sys_version = board_info_str if status == _EApiStatus.SUCCESS else str()
# print(f"- status : {status}, dmi_info_sys_version: {dmi_info_sys_version}")
# status, board_info_str = funcs.board_info_get_string(_EApiId.EAPI_ID_BOARD_DMISYS_SERIAL_STR)
# dmi_info_sys_serial = board_info_str if status == _EApiStatus.SUCCESS else str()
# print(f"- status : {status}, dmi_info_sys_serial: {dmi_info_sys_serial}")
# status, board_info_str = funcs.board_info_get_string(_EApiId.EAPI_ID_BOARD_DMIBOARD_VENDOR_STR)
# dmi_info_board_vendor = board_info_str if status == _EApiStatus.SUCCESS else str()
# print(f"- status : {status}, dmi_info_board_vendor: {dmi_info_board_vendor}")
# status, board_info_str = funcs.board_info_get_string(_EApiId.EAPI_ID_BOARD_DMIBOARD_NAME_STR)
# dmi_info_board_name = board_info_str if status == _EApiStatus.SUCCESS else str()
# print(f"- status : {status}, dmi_info_board_name: {dmi_info_board_name}")
# status, board_info_str = funcs.board_info_get_string(_EApiId.EAPI_ID_BOARD_DMIBOARD_VERSION_STR)
# dmi_info_board_version = board_info_str if status == _EApiStatus.SUCCESS else str()
# print(f"- status : {status}, dmi_info_board_version: {dmi_info_board_version}")
# status, board_info_str = funcs.board_info_get_string(_EApiId.EAPI_ID_BOARD_DMIBOARD_SERIAL_STR)
# dmi_info_board_serial = board_info_str if status == _EApiStatus.SUCCESS else str()
# print(f"- status : {status}, dmi_info_board_serial: {dmi_info_board_serial}")
# status, board_info_str = funcs.board_info_get_string(_EApiId.EAPI_ID_BOARD_DMIBOARD_ASSET_TAG_STR)
# dmi_info_board_asset_tag = board_info_str if status == _EApiStatus.SUCCESS else str()
# print(f"- status : {status}, dmi_info_board_asset_tag: {dmi_info_board_asset_tag}")

###################################################################

from advantech.edge._internal._eapi._eapi_ids import _EApiId
from advantech.edge._internal._eapi._eapi_status import _EApiStatus
from advantech.edge._internal._eapi._eapi import _EApi, WatchdogCap

eapi = _EApi()

# Get capability of feature : Platform Information
print(f"Platform Information : {'Supported' if eapi.is_platform_information_supported else 'Not Supported'}")
print(f"-\tmotherboard_name : {eapi.platform_info_data.motherboard_name}")
print(f"-\tmanufacturer : {eapi.platform_info_data.manufacturer}")
print(f"-\tboot_up_times : {eapi.platform_info_data.boot_up_times}")
print(f"-\trunning_time_in_hours : {eapi.platform_info_data.running_time_in_hours}")
print(f"-\tbios_revision : {eapi.platform_info_data.bios_revision}")
print(f"-\tfirmware_name : {eapi.platform_info_data.firmware_name}")
print(f"-\tfirmware_version : {eapi.platform_info_data.firmware_version}")
print(f"-\tlibrary_version : {eapi.platform_info_data.library_version}")
print(f"-\tdriver_version : {eapi.platform_info_data.driver_version}")
print(f"-\tec_revision : {eapi.platform_info_data.ec_revision}")
if eapi.platform_info_data.dmi_info is not None:
    print(f"-\tDMI information : ")
    print(f"-\t\tbios_vendor : {eapi.platform_info_data.dmi_info.bios_vendor}")
    print(f"-\t\tbios_version : {eapi.platform_info_data.dmi_info.bios_version}")
    print(f"-\t\tbios_release_date : {eapi.platform_info_data.dmi_info.bios_release_date}")
    print(f"-\t\tsys_uuid : {eapi.platform_info_data.dmi_info.sys_uuid}")
    print(f"-\t\tsys_vendor : {eapi.platform_info_data.dmi_info.sys_vendor}")
    print(f"-\t\tsys_product : {eapi.platform_info_data.dmi_info.sys_product}")
    print(f"-\t\tsys_version : {eapi.platform_info_data.dmi_info.sys_version}")
    print(f"-\t\tsys_serial : {eapi.platform_info_data.dmi_info.sys_serial}")
    print(f"-\t\tboard_vendor : {eapi.platform_info_data.dmi_info.board_vendor}")
    print(f"-\t\tboard_name : {eapi.platform_info_data.dmi_info.board_name}")
    print(f"-\t\tboard_version : {eapi.platform_info_data.dmi_info.board_version}")
    print(f"-\t\tboard_serial : {eapi.platform_info_data.dmi_info.board_serial}")
    print(f"-\t\tboard_asset_tag : {eapi.platform_info_data.dmi_info.board_asset_tag}")

print()

# Get capability of feature : Onboard Sensors
print(f"Onboard Sensors : {'Supported' if eapi.is_onboard_sensors_supported else 'Not Supported'}")
print(f"- temperature sources : {eapi.onboard_sensors_temperature_sources}")
print()
print(f"- voltage sources : {eapi.onboard_sensors_voltage_sources}")
print()
print(f"- fan sources : {eapi.onboard_sensors_fan_sources}")
print()

# Get capability of feature : GPIO
print(f"GPIO : {'Supported' if eapi.is_gpio_supported else 'Not Supported'}")
print(f"- pins : {eapi.gpio_pins}")
print(f"- max_pin_num : {eapi.gpio_max_pin_num}")
print()

# Get capability of feature : Watchdog
print(f"Watchdog : {'Supported' if eapi.is_watchdog_supported else 'Not Supported'}")
watchdog_cap = eapi.watchdog_cap
if watchdog_cap != None:
    print(f"- max_delay: {watchdog_cap.max_delay_in_ms} ms")
    print(f"- max_event_timeout: {watchdog_cap.max_event_timeout_in_ms} ms")
    print(f"- max_reset_timeout: {watchdog_cap.max_reset_timeout_in_ms} ms")