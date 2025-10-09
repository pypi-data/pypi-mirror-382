from typing import Union

class DmiInfo:
    """
    A class to represent DMI (Desktop Management Interface) information.
    Attributes:
        bios_vendor (str | None): BIOS vendor.
        bios_version (str | None): BIOS version.
        bios_release_date (str | None): BIOS release date.
        sys_uuid (str | None): System UUID.
        sys_vendor (str | None): System vendor.
        sys_product (str | None): System product.
        sys_version (str | None): System version.
        sys_serial (str | None): System serial number.
        board_vendor (str | None): Board vendor.
        board_name (str | None): Board name.
        board_version (str | None): Board version.
        board_serial (str | None): Board serial number.
        board_asset_tag (str | None): Board asset tag.
    """
    
    def __init__(self,
                 bios_vendor: Union[str, None] = None,
                 bios_version: Union[str, None] = None,
                 bios_release_date: Union[str, None] = None,
                 sys_uuid: Union[str, None] = None,
                 sys_vendor: Union[str, None] = None,
                 sys_product: Union[str, None] = None,
                 sys_version: Union[str, None] = None,
                 sys_serial: Union[str, None] = None,
                 board_vendor: Union[str, None] = None,
                 board_name: Union[str, None] = None,
                 board_version: Union[str, None] = None,
                 board_serial: Union[str, None] = None,
                 board_asset_tag: Union[str, None] = None):
        """
        Initialize the DmiInfo class with BIOS and system information.
        Args:
            bios_vendor (str | None): BIOS vendor.
            bios_version (str | None): BIOS version.
            bios_release_date (str | None): BIOS release date.
            sys_uuid (str | None): System UUID.
            sys_vendor (str | None): System vendor.
            sys_product (str | None): System product.
            sys_version (str | None): System version.
            sys_serial (str | None): System serial number.
            board_vendor (str | None): Board vendor.
            board_name (str | None): Board name.
            board_version (str | None): Board version.
            board_serial (str | None): Board serial number.
            board_asset_tag (str | None): Board asset tag.
        """
        self.__bios_vendor = bios_vendor
        self.__bios_version = bios_version
        self.__bios_release_date = bios_release_date
        self.__sys_uuid = sys_uuid
        self.__sys_vendor = sys_vendor
        self.__sys_product = sys_product
        self.__sys_version = sys_version
        self.__sys_serial = sys_serial
        self.__board_vendor = board_vendor
        self.__board_name = board_name
        self.__board_version = board_version
        self.__board_serial = board_serial
        self.__board_asset_tag = board_asset_tag
    
    @property
    def bios_vendor(self) -> Union[str, None]:
        """
        Get the BIOS vendor.
        Returns:
            str: BIOS vendor.
        """
        return self.__bios_vendor

    @property
    def bios_version(self) -> Union[str, None]:
        """
        Get the BIOS version.
        Returns:
            str: BIOS version.
        """
        return self.__bios_version

    @property
    def bios_release_date(self) -> Union[str, None]:
        """
        Get the BIOS release date.
        Returns:
            str: BIOS release date.
        """
        return self.__bios_release_date

    @property
    def sys_uuid(self) -> Union[str, None]:
        """
        Get the system UUID.
        Returns:
            str: System UUID.
        """
        return self.__sys_uuid

    @property
    def sys_vendor(self) -> Union[str, None]:
        """
        Get the system vendor.
        Returns:
            str: System vendor.
        """
        return self.__sys_vendor

    @property
    def sys_product(self) -> Union[str, None]:
        """
        Get the system product.
        Returns:
            str: System product.
        """
        return self.__sys_product

    @property
    def sys_version(self) -> Union[str, None]:
        """
        Get the system version.
        Returns:
            str: System version.
        """
        return self.__sys_version

    @property
    def sys_serial(self) -> Union[str, None]:
        """
        Get the system serial number.
        Returns:
            str: System serial number.
        """
        return self.__sys_serial
    
    @property
    def board_vendor(self) -> Union[str, None]:
        """
        Get the board vendor.
        Returns:
            str: Board vendor.
        """
        return self.__board_vendor

    @property
    def board_name(self) -> Union[str, None]:
        """
        Get the board name.
        Returns:
            str: Board name.
        """
        return self.__board_name

    @property
    def board_version(self) -> Union[str, None]:
        """
        Get the board version.
        Returns:
            str: Board version.
        """
        return self.__board_version

    @property
    def board_serial(self) -> Union[str, None]:
        """
        Get the board serial number.
        Returns:
            str: Board serial number.
        """
        return self.__board_serial

    @property
    def board_asset_tag(self) -> Union[str, None]:
        """
        Get the board asset tag.
        Returns:
            str: Board asset tag.
        """
        return self.__board_asset_tag