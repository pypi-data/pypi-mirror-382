from abc import abstractmethod
from typing import Union

from .ifeature import IFeature

class IMemory(IFeature):
    """
    Interface for memory information.
    This interface provides methods to retrieve various memory-related information
    such as memory count, type, size, speed, rank, voltage, bank, manufacturing date,
    temperature, write protection, module manufacturer, part number, and specific details.
    """
    
    @property
    @abstractmethod
    def count(self) -> int:
        """
        Get the number of memory modules.
        Returns:
            int: Number of memory modules
        """
        pass

    @abstractmethod
    def get_type(self, index: int) -> Union[str, None]:
        """
        Get the type of memory module.
        Args:
            memory_number (int): The memory module number (0-indexed).
        Returns:
            str: Memory module type
        """
        pass

    @abstractmethod
    def get_module_type(self, index: int) -> Union[str, None]:
        """
        Get the module type of memory.
        Args:
            memory_number (int): The memory module number (0-indexed).
        Returns:
            str: Module type
        """
        pass

    @abstractmethod
    def get_size_in_GB(self, index: int) -> Union[int, None]:
        """
        Get the size of memory module in GB.
        Args:
            memory_number (int): The memory module number (0-indexed).
        Returns:
            int: Memory module size in GB
        """
        pass

    @abstractmethod
    def get_speed(self, index: int) -> Union[str, None]:
        """
        Get the speed of memory module.
        Args:
            memory_number (int): The memory module number (0-indexed).
        Returns:
            str: Memory module speed
        """
        pass

    @abstractmethod
    def get_rank(self, index: int) -> Union[int, None]:
        """
        Get the rank of memory module.
        Args:
            memory_number (int): The memory module number (0-indexed).
        Returns:
            int: Memory module rank
        """
        pass

    @abstractmethod
    def get_voltage(self, index: int) -> Union[float, None]:
        """
        Get the voltage of memory module.
        Args:
            memory_number (int): The memory module number (0-indexed).
        Returns:
            float: Memory module voltage
        """
        pass

    @abstractmethod
    def get_bank(self, index: int) -> Union[str, None]:
        """
        Get the bank of memory module.
        Args:
            memory_number (int): The memory module number (0-indexed).
        Returns:
            str: Memory module bank
        """
        pass

    @abstractmethod
    def get_manufacturing_date_code(self, index: int) -> Union[str, None]:
        """
        Get the manufacturing date code of memory module.
        Args:
            memory_number (int): The memory module number (0-indexed).
        Returns:
            str: Memory module manufacturing date code
        """
        pass

    @abstractmethod
    def get_temperature(self, index: int) -> Union[float, None]:
        """
        Get the temperature of memory module.
        Args:
            memory_number (int): The memory module number (0-indexed).
        Returns:
            float: Memory module temperature
        """
        pass

    @abstractmethod
    def get_write_protection(self, index: int) -> Union[str, None]:
        """
        Get the write protection status of memory module.
        Args:
            memory_number (int): The memory module number (0-indexed).
        Returns:
            str: Memory module write protection status
        """
        pass

    @abstractmethod
    def get_module_manufacturer(self, index: int) -> Union[str, None]:
        """
        Get the module manufacturer of memory.
        Args:
            memory_number (int): The memory module number (0-indexed).
        Returns:
            str: Module manufacturer
        """
        pass

    @abstractmethod
    def get_manufacturer(self, index: int) -> Union[str, None]:
        """
        Get the manufacturer of memory module.
        Args:
            memory_number (int): The memory module number (0-indexed).
        Returns:
            str: Memory module manufacturer
        """
        pass

    @abstractmethod
    def get_part_number(self, index: int) -> Union[str, None]:
        """
        Get the part number of memory module.
        Args:
            memory_number (int): The memory module number (0-indexed).
        Returns:
            str: Memory module part number
        """
        pass

    @abstractmethod
    def get_specific(self, index: int) -> Union[str, None]:
        """
        Get the specific details of memory module.
        Args:
            memory_number (int): The memory module number (0-indexed).
        Returns:
            str: Memory module specific details
        """
        pass
