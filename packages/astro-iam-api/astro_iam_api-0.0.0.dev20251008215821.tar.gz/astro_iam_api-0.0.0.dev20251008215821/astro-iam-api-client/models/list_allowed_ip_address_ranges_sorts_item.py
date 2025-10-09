from enum import Enum


class ListAllowedIpAddressRangesSortsItem(str, Enum):
    CREATEDATASC = "createdAt:asc"
    CREATEDATDESC = "createdAt:desc"
    IPADDRESSASC = "ipAddress:asc"
    IPADDRESSDESC = "ipAddress:desc"
    UPDATEDATASC = "updatedAt:asc"
    UPDATEDATDESC = "updatedAt:desc"

    def __str__(self) -> str:
        return str(self.value)
