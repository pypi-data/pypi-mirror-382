from typing import Self

import pydantic
from pydantic import constr

from parcelforce_expresslink.notifications import (
    CollectionNotifications,
    RecipientNotifications,
)
from parcelforce_expresslink.shared import PFBaseModel
from parcelforce_expresslink.types import string_type

MyPhone = str


class Contact(PFBaseModel):
    business_name: string_type(40)
    mobile_phone: str
    email_address: constr(max_length=50)
    contact_name: string_type(30)
    notifications: RecipientNotifications | None = RecipientNotifications.standard_recip()

    @property
    def notifications_str(self) -> str:
        msg = f'Recip Notifications = {self.notifications} ({self.email_address} + {self.mobile_phone})'
        return msg

    @classmethod
    def empty(cls):
        return cls(
            business_name='',
            mobile_phone='00000000000',
            email_address='',
            contact_name='',
        )


class ContactCollection(Contact):
    senders_name: string_type(25) | None = None
    telephone: MyPhone | None = None
    notifications: CollectionNotifications | None = CollectionNotifications.standard_coll()

    @property
    def notifications_str(self) -> str:
        msg = f'Collecton Notifications = {self.notifications} ({self.email_address} + {self.mobile_phone})'
        return msg

    @pydantic.model_validator(mode='after')
    def fill_nones(self):
        self.telephone = self.telephone or self.mobile_phone
        self.senders_name = self.senders_name or self.contact_name
        return self

    # @classmethod
    # def from_contact(cls, contact: Contact):
    #     return cls(
    #         **contact.model_dump(exclude={'notifications'}),
    #         senders_name=contact.contact_name,


class ContactSender(Contact):
    business_name: string_type(25) | None = None
    # business_name: constr(max_length=25)
    mobile_phone: MyPhone
    email_address: constr(max_length=50)
    contact_name: string_type(25) | None = None

    telephone: MyPhone | None = None
    senders_name: string_type(25) | None = None
    notifications: None = None

    @classmethod
    def from_recipient(cls, recipient_contact) -> Self:
        return cls(**recipient_contact.model_dump(exclude={'notifications'}))


class ContactTemporary(Contact):
    business_name: str = ''
    contact_name: str = ''
    mobile_phone: MyPhone | None = None
    email_address: str = ''
    telephone: MyPhone | None = None
    senders_name: str = ''

    @pydantic.model_validator(mode='after')
    def fake(self):
        for field, value in self.model_dump().items():
            if not value:
                value = '========='
                if field == 'email_address':
                    value = f'{value}@f======f.com'
                setattr(self, field, value)
        return self


def address_string_to_dict(address_str: str) -> dict[str, str]:
    addr_lines = address_str.splitlines()
    if len(addr_lines) < 3:
        addr_lines.extend([''] * (3 - len(addr_lines)))
    elif len(addr_lines) > 3:
        addr_lines[2] = ','.join(addr_lines[2:])
    return {
        'address_line1': addr_lines[0],
        'address_line2': addr_lines[1],
        'address_line3': addr_lines[2],
    }


class AddressBase(PFBaseModel):
    address_line1: string_type(24)
    address_line2: string_type(24) | None = None
    address_line3: string_type(24) | None = None
    town: constr(max_length=25)
    postcode: constr(max_length=16)
    country: str = 'GB'

    @property
    def lines_dict(self):
        return {
            line_field: getattr(self, line_field) for line_field in sorted(self.lines_fields_set)
        }

    @property
    def lines_fields_set(self):
        return {_ for _ in addr_lines_fields_set if getattr(self, _)}

    @property
    def lines_str(self):
        return '\n'.join(self.lines_dict.values())

    @property
    def lines_str_oneline(self):
        return ', '.join(self.lines_dict.values())


class AddressSender(AddressBase):
    @classmethod
    def from_recipient(cls, recipient: AddressBase) -> Self:
        return cls(**recipient.model_dump(exclude_none=True))


class AddressCollection(AddressSender):
    address_line1: string_type(40)
    address_line2: string_type(40) | None = None
    address_line3: string_type(40) | None = None
    town: string_type(30)


class AddressRecipient(AddressCollection):
    address_line1: string_type(40)
    address_line2: string_type(50) | None = None
    address_line3: string_type(60) | None = None
    town: string_type(30)


class AddressTemporary(AddressRecipient):
    address_line1: str | None = None
    address_line2: str | None = None
    address_line3: str | None = None
    town: str | None = None
    postcode: str | None = None


class AddressChoice[T: AddressCollection | AddressRecipient](PFBaseModel):
    address: T
    # address: T = sqm.Field(sa_column=sqm.Column(sqm.JSON))
    score: int


addr_lines_fields_set = {'address_line1', 'address_line2', 'address_line3'}
AddTypes = AddressRecipient | AddressCollection | AddressSender


def get_address_types() -> frozenset[type[AddressBase]]:
    return frozenset([AddressBase, AddressRecipient, AddressCollection, AddressSender])

def get_contact_types() -> frozenset[type[Contact]]:
    return frozenset([Contact, ContactCollection, ContactSender, ContactTemporary])