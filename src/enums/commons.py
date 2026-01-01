from enum import StrEnum


class ClientCodeTypeEnum(StrEnum):
    CHINA_NICKNAME = "CHINA_NICKNAME"
    DIGITAL = "DIGITAL"


class ShipmentStatusEnum(StrEnum):
    CREATED = "CREATED"
    IN_STOCK = "IN_STOCK"
    IN_TRANSIT = "IN_TRANSIT"
    ARRIVED = "ARRIVED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
