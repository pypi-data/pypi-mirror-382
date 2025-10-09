from ctypes import RTLD_GLOBAL
from ctypes import c_int
from ctypes import c_char_p
from ctypes import Structure

class _DiskPartInfo:
    
    def __init__(self, partition_id, partition_size, partition_name):
        self.__partition_id = partition_id
        self.__partition_size = partition_size
        self.__partition_name = partition_name
        
    @property
    def partition_id(self):
        return self.__partition_id
    
    @property
    def partition_size(self):
        return self.__partition_size
    
    @property
    def partition_name(self):
        return self.__partition_name

class _DiskInfo:
    
    def __init__(self, disk_count, disk_part_info):
        self.__disk_count = disk_count
        self.__disk_part_info = disk_part_info
        
    @property
    def disk_count(self):
        return self.__disk_count
    
    @property
    def disk_part_info(self):
        return self.__disk_part_info

class _DiskPartInfoC(Structure):
    _fields_ = [
        ("partition_id", c_int),
        ("partition_size", c_int),
        ("partition_name", c_char_p)
    ]

class _DiskInfoC(Structure):
    _fields_ = [
        ("disk_count", c_int),
        ("disk_part_info", _DiskPartInfoC * 8)  # 最多支持 8 個分區
    ]