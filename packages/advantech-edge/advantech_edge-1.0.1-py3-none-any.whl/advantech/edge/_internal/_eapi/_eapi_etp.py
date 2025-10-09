from ctypes import c_ubyte
from ctypes import Structure

class _ETP_USER_DATA(Structure):
    _fields_ = [
        ("UserSpace1", c_ubyte * 128),  # A6, offset 0
        ("UserSpace2", c_ubyte * 128)   # A6, offset 128
    ]

class _ETP_DATA(Structure):
    _fields_ = [
        ("DeviceOrderText", c_ubyte * 40),
        ("DeviceOrderNumber", c_ubyte * 10),
        ("DeviceIndex", c_ubyte * 3),
        ("DeviceSerialNumber", c_ubyte * 15),
        ("OperatingSystem", c_ubyte * 40),
        ("Image", c_ubyte * 40),
        ("Reverse", c_ubyte * 92)
    ]