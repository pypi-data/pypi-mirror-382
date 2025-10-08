from __future__ import annotations

import datetime as dt
from enum import StrEnum
from pathlib import Path
from typing import Self
from loguru import logger
from pydantic import constr

from parcelforce_expresslink.types import DropOffInd, ShipmentType
from parcelforce_expresslink.address import (
    AddressCollection,
    AddressSender,
    Contact,
    ContactCollection,
    ContactSender,
    AddressBase,
)
from parcelforce_expresslink.lists import HazardousGoods
from parcelforce_expresslink.models import AddressRecipient, DeliveryOptions
from parcelforce_expresslink.services import ServiceCode
from parcelforce_expresslink.shared import DateTimeRange, Enhancement, PFBaseModel
from parcelforce_expresslink.top import CollectionInfo


# from shipaw.models.ship_types import ShipDirection


class ShipmentReferenceFields(PFBaseModel):
    reference_number1: constr(max_length=24) | None = None
    reference_number2: constr(max_length=24) | None = None
    reference_number3: constr(max_length=24) | None = None
    reference_number4: constr(max_length=24) | None = None
    reference_number5: constr(max_length=24) | None = None
    special_instructions1: constr(max_length=25) | None = None
    special_instructions2: constr(max_length=25) | None = None
    special_instructions3: constr(max_length=25) | None = None
    special_instructions4: constr(max_length=25) | None = None


class Shipment(ShipmentReferenceFields):
    """Needs contract number and department id from settings"""

    shipment_type: ShipmentType = ShipmentType.DELIVERY
    # from settings
    department_id: int = 1
    contract_number: str

    recipient_contact: Contact
    recipient_address: AddressRecipient | AddressCollection
    total_number_of_parcels: int = 1
    shipping_date: dt.date
    service_code: ServiceCode = ServiceCode.EXPRESS24

    # collection
    print_own_label: bool | None = None
    collection_info: CollectionInfo | None = None
    # dropoff
    sender_contact: ContactSender | None = None
    sender_address: AddressSender | None = None

    _label_file: Path | None = (
        None  # must be private for xml serialization to exclude / expresslink to work
    )
    _direction: ShipDirection | None = None  # derived, not settable

    # currently unused (but required by expresslink)
    enhancement: Enhancement | None = None
    delivery_options: DeliveryOptions | None = None
    hazardous_goods: HazardousGoods | None = None
    consignment_handling: bool | None = None
    drop_off_ind: DropOffInd | None = None

    @property
    def direction(self) -> ShipDirection:
        if self.shipment_type == ShipmentType.DELIVERY:
            if self.sender_address is None:
                return ShipDirection.OUTBOUND
            else:
                return ShipDirection.DROPOFF
        elif self.shipment_type == ShipmentType.COLLECTION:
            return ShipDirection.INBOUND
        else:
            raise ValueError()

    def swap_sender_recipient(self, *, recipient_address, recipient_contact) -> Self:
        """ie for Dropoff, or first step to inbound collection"""
        if self.direction != ShipDirection.OUTBOUND:
            raise ValueError('Can only convert outbound delivery shipments')
        res = self.model_copy(deep=True)
        res.recipient_address = recipient_address
        res.recipient_contact = recipient_contact
        res.sender_contact = ContactSender.from_recipient(self.recipient_contact)
        res.sender_address = AddressSender.from_recipient(self.recipient_address)
        return res

    def change_sender_to_collection(self):
        """ASSUMES ALREADY HAS SENDER AND OWN_LABEL SET - USE swap_sender_recipient FIRST"""
        self.shipment_type = ShipmentType.COLLECTION
        self.collection_info = collection_info_from_deets(
            address=self.sender_address,
            contact=self.sender_contact,
            shipping_date=self.shipping_date,
        )
        self.sender_address = None
        self.sender_contact = None
        logger.warning(
            'In place conversion to inbound collection, mutating self, setting collection and erasing sender'
        )
        return self

    def convert(self, *, recipient_address, recipient_contact, direction: ShipDirection) -> Self:
        if direction == ShipDirection.OUTBOUND:
            raise ValueError('Can not convert to OUTBOUND, only INBOUND or DROPOFF')
        if self.direction != ShipDirection.OUTBOUND:
            raise ValueError('Can only convert outbound delivery shipments')
        res = self.swap_sender_recipient(
            recipient_address=recipient_address, recipient_contact=recipient_contact
        )
        if direction == ShipDirection.INBOUND:
            res.change_sender_to_collection()

    def __str__(self):
        return f'{self.shipment_type} {f'from {self.collection_info.collection_address.address_line1} ' if self.collection_info else ''}to {self.recipient_address.address_line1}'


def collection_info_from_recipient(shipment):
    return CollectionInfo(
        collection_address=AddressCollection(**shipment.recipient_address.model_dump()),
        collection_contact=(
            ContactCollection.model_validate(
                shipment.recipient_contact.model_dump(exclude={'notifications'})
            )
        ),
        collection_time=DateTimeRange.null_times_from_date(shipment.shipping_date),
    )


def collection_info_from_deets(address: AddressBase, contact: Contact, shipping_date: dt.date):
    return CollectionInfo(
        collection_address=AddressCollection.model_validate(address, from_attributes=True),
        collection_contact=(
            ContactCollection.model_validate(contact.model_dump(exclude={'notifications'}))
        ),
        collection_time=DateTimeRange.null_times_from_date(shipping_date),
    )


def collection_info_from_sender(shipment):
    return CollectionInfo(
        collection_address=AddressCollection(**shipment.sender_address.model_dump()),
        collection_contact=(
            ContactCollection.model_validate(
                shipment.sender_contact.model_dump(exclude={'notifications'})
            )
        ),
        collection_time=DateTimeRange.null_times_from_date(shipment.shipping_date),
    )


class ShipDirection(StrEnum):
    INBOUND = 'in'
    OUTBOUND = 'out'
    DROPOFF = 'dropoff'

