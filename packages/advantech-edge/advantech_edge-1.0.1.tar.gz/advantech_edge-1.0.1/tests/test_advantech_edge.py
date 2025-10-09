import unittest

import sys
sys.path.append('..')

from advantech.edge import Device
from advantech.edge.ifeatures import GpioDirectionTypes, GpioLevelTypes

class TestPlatformInformation(unittest.TestCase):
    
    def test_platform_information(self):
        
        print("\n------------------------------------")
        
        device = Device()
        
        print(f"Device description : {device.description}")
        print(f"Motherboard manufacturer : {device.platform_information.manufacturer}")
        print(f"Motherboard name : {device.platform_information.motherboard_name}")
        print(f"BIOS revision : {device.platform_information.bios_revision}")
        print(f"Library version : {device.platform_information.library_version}")
        dmi_info = device.platform_information.dmi_info
        if dmi_info is not None:
            print(f"DMI Information : ")
            print(f"-\tBIOS vendor : {dmi_info.bios_vendor}")
            print(f"-\tBIOS version : {dmi_info.bios_version}")
            print(f"-\tBIOS release date : {dmi_info.bios_release_date}")
            print(f"-\tBIOS system UUID : {dmi_info.sys_uuid}")
            print(f"-\tSystem vendor : {dmi_info.sys_vendor}")
            print(f"-\tSystem product : {dmi_info.sys_product}")
            print(f"-\tSystem version : {dmi_info.sys_version}")
            print(f"-\tSystem serial : {dmi_info.sys_serial}")
            print(f"-\tBoard vendor : {dmi_info.board_vendor}")
            print(f"-\tBoard name : {dmi_info.board_name}")
            print(f"-\tBoard version : {dmi_info.board_version}")
            print(f"-\tBoard serial : {dmi_info.board_serial}")
            print(f"-\tBoard asset tag : {dmi_info.board_asset_tag}")
        
        print("------------------------------------")

class TestOnboardSensors(unittest.TestCase):
    
    def test_onboard_sensors(self):
        
        print("\n------------------------------------")
        
        device = Device()
        
        if device.onboard_sensors.is_supported:
        
            print(f"Temperature source number : {len(device.onboard_sensors.temperature_sources)}")
            for src in device.onboard_sensors.temperature_sources:
                print(f"- {src} : {device.onboard_sensors.get_temperature(src)} degrees Celsius")
            
            print()
            
            print(f"Voltage source number : {len(device.onboard_sensors.voltage_sources)}")
            for src in device.onboard_sensors.voltage_sources:
                print(f"- {src} : {device.onboard_sensors.get_voltage(src)} volts")
            
            print()
            
            print(f"Fan speed source number : {len(device.onboard_sensors.fan_sources)}")
            for src in device.onboard_sensors.fan_sources:
                print(f"- {src} : {device.onboard_sensors.get_fan_speed(src)} RPM")
        
        else:
            
            print(f"Onboard sensors : not supported.")
            
        print("------------------------------------")

    def test_invalid_temperature_source(self):
        
        print("\n------------------------------------")
        
        device = Device()
        
        if device.onboard_sensors.is_supported:
            
            # Test : Invalid input
            temperature = device.onboard_sensors.get_temperature("Invalid source")
            self.assertEqual(temperature, None, "Test case fail : invalid source string")
            
            print(f"Test pass.")
        
        else:
            
            print(f"Onboard sensors : not supported.")
            
        print("------------------------------------")
    
    def test_invalid_voltage_source(self):
        
        print("\n------------------------------------")
        
        device = Device()
        
        if device.onboard_sensors.is_supported:
            
            # Test : Invalid input
            voltage = device.onboard_sensors.get_voltage("Invalid source")
            self.assertEqual(voltage, None, "Test case fail : invalid source string")
            
            print(f"Test pass.")
        
        else:
            
            print(f"Onboard sensors : not supported.")
            
        print("------------------------------------")

    def test_invalid_fan_source(self):
        
        print("\n------------------------------------")
        
        device = Device()
        
        if device.onboard_sensors.is_supported:
            
            # Test : Invalid input
            fan_speed = device.onboard_sensors.get_fan_speed("Invalid source")
            self.assertEqual(fan_speed, None, "Test case fail : invalid source string")
            
            print(f"Test pass.")
        
        else:
            
            print(f"Onboard sensors : not supported.")
            
        print("------------------------------------")

class TestGpio(unittest.TestCase):
    
    def test_pin_number_equality(self):
        
        print("\n------------------------------------")
        
        device = Device()
        
        if device.gpio.is_supported:
            
            # Test : number of pins
            pin_num_1 = device.gpio.max_pin_num
            pin_num_2 = len(device.gpio.pin_names)
            self.assertEqual(pin_num_1, pin_num_2, f"Test case fail : number of pins not equal")
            
            print(f"Test pass.")
            
        else:
            
            print(f"GPIO : not supported.")
        
        print("------------------------------------")
    
    def test_get_pin_states_by_name(self):
        
        print("\n------------------------------------")
        
        device = Device()
        
        if device.gpio.is_supported:
        
            for pin_name in device.gpio.pin_names:
                
                try:
                    
                    pin_dir = device.gpio.get_direction(pin_name)
                    if pin_dir is None:
                        raise RuntimeError(f"{pin_name} - fail to get pin direction")
                    
                    pin_level = device.gpio.get_level(pin_name)
                    if pin_level is None:
                        raise RuntimeError(f"{pin_name} - fail to get pin level")
                    
                    print(f"{pin_name} - direction : {pin_dir.name}, level : {pin_level.name}")
                
                except Exception as e:
                    
                    print(f"{e}")
                
        else:
            
            print(f"GPIO : not supported.")
        
        print("------------------------------------")

    def test_get_pin_states_by_invalid_name(self):
        
        print("\n------------------------------------")
        
        device = Device()
        
        if device.gpio.is_supported:
        
            pin_name = "Invalid pin"
            
            pin_dir = device.gpio.get_direction(pin_name)
            self.assertEqual(pin_dir, None, f"Test fail - direction not equal to None")
                    
            pin_level = device.gpio.get_level(pin_name)
            self.assertEqual(pin_level, None, f"Test fail - level not equal to None")
                    
            print(f"Test passed.")
                
        else:
            
            print(f"GPIO : not supported.")
        
        print("------------------------------------")

    def test_get_pin_states_by_index(self):
        
        print("\n------------------------------------")
        
        device = Device()
        
        if device.gpio.is_supported:
            
            max_pin_num = device.gpio.max_pin_num
            print(f"Max pin number : {max_pin_num}")
            
            for pin_index in range(max_pin_num):
                
                try:
                    
                    # Check if pin index is out of range.
                    if pin_index >= len(device.gpio.pin_names):
                        self.fail(f"Pin index out of range : {pin_index}, \
                                  max_pin_num : {device.gpio.max_pin_num}, \
                                  length of pin_names : {len(device.gpio.pin_names)}")
                    
                    # Get pin name by index
                    pin_name = device.gpio.pin_names[pin_index]
                    
                    # Get pin direction by index
                    pin_dir = device.gpio.get_direction(pin_index)
                    if pin_dir is None:
                        raise RuntimeError(f"{pin_name} (index : {pin_index}) - fail to get pin direction.")
                
                    pin_level = device.gpio.get_level(pin_index)
                    if pin_level is None:
                        raise RuntimeError(f"{pin_name} (index : {pin_index}) - fail to get pin level.")
                
                    print(f"{pin_name} (index : {pin_index}) - direction : {pin_dir.name}, level : {pin_level.name}")
                    
                except Exception as e:
                    
                    print(f"{e}")
                
        else:
            
            print(f"GPIO : not supported.")
        
        print("------------------------------------")
    
    def test_get_pin_states_by_invalid_index(self):
        
        print("\n------------------------------------")
        
        device = Device()
        
        if device.gpio.is_supported:
        
            pin_index = -1
            
            pin_dir = device.gpio.get_direction(pin_index)
            self.assertEqual(pin_dir, None, f"Test fail - direction not equal to None")
                    
            pin_level = device.gpio.get_level(pin_index)
            self.assertEqual(pin_level, None, f"Test fail - level not equal to None")
                    
            print(f"Test passed.")
                
        else:
            
            print(f"GPIO : not supported.")
        
        print("------------------------------------")
    
    def test_set_pin_dir_by_name(self):
        
        print("\n------------------------------------")
        
        device = Device()
        
        if device.gpio.is_supported:
        
            for pin_name in device.gpio.pin_names:
                
                try:
                    
                    # Get direction before set.
                    pin_dir = device.gpio.get_direction(pin_name)
                    if pin_dir is None:
                        raise RuntimeError(f"{pin_name} - fail to get direction before set.")
                    pin_dir_1 = pin_dir
                
                    # Determine direction to be set (opposite direction)
                    if pin_dir_1 == GpioDirectionTypes.Input:
                        pin_dir_new = GpioDirectionTypes.Output
                    elif pin_dir_1 == GpioDirectionTypes.Output:
                        pin_dir_new = GpioDirectionTypes.Input
                    else:
                        continue
                
                    # Set direction.
                    device.gpio.set_direction(pin_name, pin_dir_new)
                
                    # Get direction after set.
                    pin_dir = device.gpio.get_direction(pin_name)
                    if pin_dir is None:
                        raise RuntimeError(f"{pin_name} - fail to get direction after set.")
                    pin_dir_2 = pin_dir
                
                    # Restore direction to unset state.
                    device.gpio.set_direction(pin_name, pin_dir_1)
                    
                    # Get direction after restored.
                    pin_dir = device.gpio.get_direction(pin_name)
                    if pin_dir is None:
                        raise RuntimeError(f"{pin_name} - fail to get direction after restored.")
                    pin_dir_3 = pin_dir
                
                    # Print direction info.
                    print(f"{pin_name} : {pin_dir_1.name} -> {pin_dir_2.name} -> {pin_dir_3.name}")
                
                except Exception as e:
                    
                    print(f"{e}")         
        
        else:
            
            print(f"GPIO : not supported.")
        
        print("------------------------------------")

    def test_set_pin_dir_by_invalid_name(self):
        
        print("\n------------------------------------")
        
        device = Device()
        
        if device.gpio.is_supported:
            
            try:
                pin_name = "Invalid pin name"
                device.gpio.set_direction(pin_name, GpioDirectionTypes.Input)
                self.fail(f"Test failed, exception not raised.")
            except Exception as e:
                print(f"Test passed.")
        
        else:
            
            print(f"GPIO : not supported.")
        
        print("------------------------------------")

    def test_set_pin_dir_by_index(self):
        
        print("\n------------------------------------")
        
        device = Device()
        
        if device.gpio.is_supported:
            
            max_pin_num = device.gpio.max_pin_num
            print(f"Max pin number : {max_pin_num}")
        
            for pin_index in range(max_pin_num):
                
                try:
                    
                    # Check if pin index is out of range.
                    if pin_index >= len(device.gpio.pin_names):
                        self.fail(f"Pin index out of range : {pin_index}, \
                                  max_pin_num : {device.gpio.max_pin_num}, \
                                  length of pin_names : {len(device.gpio.pin_names)}")
                    
                    # Get pin name
                    pin_name = device.gpio.pin_names[pin_index]
                
                    # Get direction before set.
                    pin_dir = device.gpio.get_direction(pin_index)
                    if pin_dir is None:
                        raise RuntimeError(f"{pin_name} (index : {pin_index}) - fail to get direction before set.")
                    pin_dir_1 = pin_dir
                
                    # Determine direction to be set (opposite direction)
                    if pin_dir_1 == GpioDirectionTypes.Input:
                        pin_dir_new = GpioDirectionTypes.Output
                    elif pin_dir_1 == GpioDirectionTypes.Output:
                        pin_dir_new = GpioDirectionTypes.Input
                    else:
                        continue
                
                    # Set direction.
                    device.gpio.set_direction(pin_index, pin_dir_new)
                    
                    # Get direction after set.
                    pin_dir = device.gpio.get_direction(pin_index)
                    if pin_dir is None:
                        raise RuntimeError(f"{pin_name} (index : {pin_index}) - fail to get direction after set.")
                    pin_dir_2 = pin_dir
                    
                    # Restore direction to unset state.
                    device.gpio.set_direction(pin_index, pin_dir_1)
                    
                    # Get direction after restored.
                    pin_dir = device.gpio.get_direction(pin_index)
                    if pin_dir is None:
                        raise RuntimeError(f"{pin_name} (index : {pin_index}) - fail to get direction after restored.")
                    pin_dir_3 = pin_dir
                    
                    # Print direction info.
                    print(f"{pin_name} (index : {pin_index}) : {pin_dir_1.name} -> {pin_dir_2.name} -> {pin_dir_3.name}")
                    
                except Exception as e:
                    
                    print(f"{e}")
        
        else:
            
            print(f"GPIO : not supported.")
        
        print("------------------------------------")

    def test_set_pin_dir_by_invalid_index(self):
        
        print("\n------------------------------------")
        
        device = Device()
        
        if device.gpio.is_supported:
            
            try:
                pin_index = -1
                device.gpio.set_direction(pin_index, GpioDirectionTypes.Input)
                self.fail(f"Test failed, exception not raised.")
            except Exception as e:
                print(f"Test passed.")
        
        else:
            
            print(f"GPIO : not supported.")
        
        print("------------------------------------")

    def test_set_pin_level_by_name(self):
        
        print("\n------------------------------------")
        
        device = Device()
        
        if device.gpio.is_supported:
        
            for pin_name in device.gpio.pin_names:
                
                try:
                    
                    # Get direction before set.
                    pin_dir = device.gpio.get_direction(pin_name)
                    if pin_dir is None:
                        raise RuntimeError(f"{pin_name} - fail to get direction before set.")
                    pin_dir_before = pin_dir
                    
                    # Set direction to OUTPUT mode.
                    device.gpio.set_direction(pin_name, GpioDirectionTypes.Output)
                    
                    # Get level before set.
                    pin_level = device.gpio.get_level(pin_name)
                    if pin_level is None:
                        raise RuntimeError(f"{pin_name} - fail to get level before set.")
                    pin_level_1 = pin_level
                    
                    # Determine level before set.
                    if pin_level_1 == GpioLevelTypes.High:
                        pin_level_new = GpioLevelTypes.Low
                    elif pin_level_1 == GpioLevelTypes.Low:
                        pin_level_new = GpioLevelTypes.High
                    else:
                        continue
                    
                    # Set level
                    device.gpio.set_level(pin_name, pin_level_new)
                    
                    # Get level after set.
                    pin_level = device.gpio.get_level(pin_name)
                    if pin_level is None:
                        raise RuntimeError(f"{pin_name} - fail to get level after set.")
                    pin_level_2 = pin_level

                    # Restore level to unset state.
                    device.gpio.set_level(pin_name, pin_level_1)
                    
                    # Get level after restored.
                    pin_level = device.gpio.get_level(pin_name)
                    if pin_level is None:
                        raise RuntimeError(f"{pin_name} - fail to get level after restored.")
                    pin_level_3 = pin_level
                    
                    # Restore direction to unset state.
                    device.gpio.set_direction(pin_name, pin_dir_before)
                    
                    # Print level information.
                    print(f"{pin_name} : {pin_level_1.name} -> {pin_level_2.name} -> {pin_level_3.name}")
                    
                except Exception as e:
                    
                    print(f"{e}")
                
        else:
            
            print(f"GPIO : not supported.")
        
        print("------------------------------------")

    def test_set_pin_level_by_invalid_name(self):
        
        print("\n------------------------------------")
        
        device = Device()
        
        if device.gpio.is_supported:
            
            try:
                pin_name = "Invalid pin name"
                device.gpio.set_level(pin_name, GpioLevelTypes.High)
                self.fail(f"Test failed, exception not raised.")
            except Exception as e:
                print(f"Test passed.")
        
        else:
            
            print(f"GPIO : not supported.")
        
        print("------------------------------------")

    def test_set_pin_level_by_index(self):
        
        print("\n------------------------------------")
        
        device = Device()
        
        if device.gpio.is_supported:
            
            max_pin_num = device.gpio.max_pin_num
            print(f"Max pin number : {max_pin_num}")
        
            for pin_index in range(max_pin_num):
                
                try:
                    
                    # Check if pin index is out of range.
                    if pin_index >= len(device.gpio.pin_names):
                        self.fail(f"Pin index out of range : {pin_index}, \
                                  max_pin_num : {device.gpio.max_pin_num}, \
                                  length of pin_names : {len(device.gpio.pin_names)}")
                    
                    # Get pin name
                    pin_name = device.gpio.pin_names[pin_index]
                    
                    # Get direction before set.
                    pin_dir = device.gpio.get_direction(pin_index)
                    if pin_dir is None:
                        raise RuntimeError(f"{pin_name} (index : {pin_index}) - fail to get direction before set.")
                    pin_dir_before = pin_dir
                    
                    # Set direction to OUTPUT mode.
                    device.gpio.set_direction(pin_index, GpioDirectionTypes.Output)
                    
                    # Get level before set.
                    pin_level = device.gpio.get_level(pin_index)
                    if pin_level is None:
                        raise RuntimeError(f"{pin_name} (index : {pin_index}) - fail to get level before set.")
                    pin_level_1 = pin_level
                    
                    # Determine level before set.
                    if pin_level_1 == GpioLevelTypes.High:
                        pin_level_new = GpioLevelTypes.Low
                    elif pin_level_1 == GpioLevelTypes.Low:
                        pin_level_new = GpioLevelTypes.High
                    else:
                        continue
                    
                    # Set level
                    device.gpio.set_level(pin_index, pin_level_new)
                    
                    # Get level after set.
                    pin_level = device.gpio.get_level(pin_index)
                    if pin_level is None:
                        raise RuntimeError(f"{pin_name} (index : {pin_index}) - fail to get level after set.")
                    pin_level_2 = pin_level

                    # Restore level to unset state.
                    device.gpio.set_level(pin_index, pin_level_1)
                    
                    # Get level after restored.
                    pin_level = device.gpio.get_level(pin_index)
                    if pin_level is None:
                        raise RuntimeError(f"{pin_name} (index : {pin_index}) - fail to get level after restored.")
                    pin_level_3 = pin_level
                    
                    # Restore direction to unset state.
                    device.gpio.set_direction(pin_index, pin_dir_before)
                    
                    # Print level information.
                    print(f"{pin_name} (index : {pin_index}) : {pin_level_1.name} -> {pin_level_2.name} -> {pin_level_3.name}")
                    
                except Exception as e:
                    
                    print(f"{e}")
                
        else:
            
            print(f"GPIO : not supported.")
        
        print("------------------------------------")

    def test_set_pin_level_by_invalid_index(self):
        
        print("\n------------------------------------")
        
        device = Device()
        
        if device.gpio.is_supported:
            
            try:
                pin_index = -1
                device.gpio.set_level(pin_index, GpioLevelTypes.High)
                self.fail(f"Test failed, exception not raised.")
            except Exception as e:
                print(f"Test passed.")
        
        else:
            
            print(f"GPIO : not supported.")
        
        print("------------------------------------")

class TestWatchdog(unittest.TestCase):
    
    def test_watchdog_cap(self):
        
        print("\n------------------------------------")
        
        device = Device()
        
        if device.watchdog.is_supported:
            
            print(f"Watchdog : supported.")
        
        else:
            
            print(f"Watchdog : not supported.")
        
        print("------------------------------------")

class TestSDRAM(unittest.TestCase):
    
    def test_sdram_info(self):
        
        print("\n------------------------------------")
        
        device = Device()
        
        if device.memory.is_supported:
            
            print(f"memory count: {device.memory.count}")
            for i in range(device.memory.count):
                print(f"Memory {i} :")
                print(f"-\ttype : {device.memory.get_type(i)}")
                print(f"-\tmodule type : {device.memory.get_module_type(i)}")
                print(f"-\tsize in GB : {device.memory.get_size_in_GB(i)}")
                print(f"-\tspeed : {device.memory.get_speed(i)} MT/s")
                print(f"-\trank : {device.memory.get_rank(i)}")
                print(f"-\tvoltage : {device.memory.get_voltage(i)} v")
                print(f"-\tbank : {device.memory.get_bank(i)}")
                print(f"-\tmanufacturing date code week/year : {device.memory.get_manufacturing_date_code(i)}")
                print(f"-\ttemperature : {device.memory.get_temperature(i)} degrees Celsius")
                print(f"-\twrite protection : {device.memory.get_write_protection(i)}")
                print(f"-\tmodule manufacture : {device.memory.get_module_manufacturer(i)}")
                print(f"-\tmanufacture : {device.memory.get_manufacturer(i)}")
                print(f"-\tpart number : {device.memory.get_part_number(i)}")
                print(f"-\tspecific : {device.memory.get_specific(i)}")
                
        else:
            
            print(f"Memory : not supported.")
        
        print("------------------------------------")
            
class TestDiskInfo(unittest.TestCase):

    def test_disk_info(self):
        
        print("\n------------------------------------")
        
        device = Device()
        
        if device.disk_info.is_supported:
            
            for disk in device.disk_info.disks:
                
                total_space = device.disk_info.get_total_space(disk)
                free_space = device.disk_info.get_free_space(disk)
            
                print(f"{disk} - Total space : {total_space} MB, Free space : {free_space} MB")
            
        else:
            
            print(f"Disk Information : not supported.")
        
        print("------------------------------------")

if __name__ == '__main__':
    unittest.main()