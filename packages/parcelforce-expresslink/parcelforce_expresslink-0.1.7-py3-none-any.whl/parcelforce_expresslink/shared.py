# from __future__ import annotations
import datetime as dt
from enum import Enum
from pathlib import Path

import pydantic as _p
from pydantic import BaseModel, ConfigDict, AliasGenerator
from pydantic.alias_generators import to_pascal


class PFBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            alias=to_pascal,
        ),
        populate_by_name=True,
        use_enum_values=True,
    )


class Hours(PFBaseModel):
    open: str | None = None
    close: str | None = None
    close_lunch: str | None = None
    after_lunch_opening: str | None = None


class DayHours(PFBaseModel):
    hours: Hours | None = None


class OpeningHours(PFBaseModel):
    mon: DayHours | None = None
    tue: DayHours | None = None
    wed: DayHours | None = None
    thu: DayHours | None = None
    fri: DayHours | None = None
    sat: DayHours | None = None
    sun: DayHours | None = None
    bank_hol: DayHours | None = None


class HazardousGood(PFBaseModel):
    lqdgun_code: str | None = None
    lqdg_description: str | None = None
    lqdg_volume: float | None = None
    firearms: str | None = None


class Returns(PFBaseModel):
    returns_email: str | None = None
    email_message: str | None = None
    email_label: bool


class ContentDetail(PFBaseModel):
    country_of_manufacture: str
    country_of_origin: str | None = None
    manufacturers_name: str | None = None
    description: str
    unit_weight: float
    unit_quantity: int
    unit_value: float
    currency: str
    tariff_code: str | None = None
    tariff_description: str | None = None
    article_reference: str | None = None


class DateTimeRange(PFBaseModel):
    from_: str = _p.Field(alias='From')
    to: str

    @classmethod
    def null_times_from_date(cls, null_date: dt.date):
        null_isodatetime = dt.datetime.combine(null_date, dt.time(0, 0)).isoformat(
            timespec='seconds'
        )
        return cls(from_=null_isodatetime, to=null_isodatetime)

    @classmethod
    def from_datetimes(cls, from_dt: dt.datetime, to_dt: dt.datetime):
        return cls(
            from_=from_dt.isoformat(timespec='seconds'), to=to_dt.isoformat(timespec='seconds')
        )


class ContentData(PFBaseModel):
    name: str
    data: str


class LabelItem(PFBaseModel):
    name: str
    data: str


class Barcode(PFBaseModel):
    name: str
    data: str


class Image(PFBaseModel):
    name: str
    data: str


class ManifestShipment(PFBaseModel):
    shipment_number: str
    service_code: str


class CompletedShipment(PFBaseModel):
    shipment_number: str | None = None
    out_bound_shipment_number: str | None = None
    in_bound_shipment_number: str | None = None
    partner_number: str | None = None


class CompletedCancelInfo(PFBaseModel):
    status: str | None = None
    shipment_number: str | None = None


class Position(PFBaseModel):
    longitude: float | None = None
    latitude: float | None = None


class Document(PFBaseModel):
    data: bytes

    def download(self, outpath: Path) -> Path:
        with open(outpath, 'wb') as f:
            f.write(self.data)
        return Path(outpath)


class Enhancement(PFBaseModel):
    enhanced_compensation: str | None = None
    saturday_delivery_required: bool | None = None


#     ALSO IN MSG?!
# class Alert(PFBaseModel):
#     code: int | None = None
#     message: str
#     type: AlertType
#
#
#     @classmethod
#     def from_exception(cls, e: Exception):
#         return cls(message=str(e), type='ERROR')


class NotificationType(str, Enum):
    EMAIL = 'EMAIL'
    EMAIL_DOD_INT = 'EMAILDODINT'
    EMAIL_ATTEMPT = 'EMAILATTEMPTDELIVERY'
    EMAIL_COLL_REC = 'EMAILCOLLRECEIVED'
    EMAIL_START_DEL = 'EMAILSTARTOFDELIVERY'
    DELIVERY = 'DELIVERYNOTIFICATION'
    SMS_DOD = 'SMSDAYOFDESPATCH'
    SMS_START_DEL = 'SMSSTARTOFDELIVERY'
    SMS_ATTEMPT_DEL = 'SMSATTEMPTDELIVERY'
    SMS_COLL_REC = 'SMSCOLLRECEIVED'


notification_label_map = {
    NotificationType.EMAIL: 'Email',
    NotificationType.EMAIL_DOD_INT: 'Email Day of Delivery Interactive',
    NotificationType.EMAIL_ATTEMPT: 'Email Attempted Delivery',
    NotificationType.EMAIL_COLL_REC: 'Email Collection Received',
    NotificationType.EMAIL_START_DEL: 'Email Start of Delivery',
    NotificationType.DELIVERY: 'Email Delivery',
    NotificationType.SMS_DOD: 'SMS Day of Despatch',
    NotificationType.SMS_START_DEL: 'SMS Start of Delivery',
    NotificationType.SMS_ATTEMPT_DEL: 'SMS Attempted Delivery',
    NotificationType.SMS_COLL_REC: 'SMS Collection Received',
}


#
# notification_label_map = {
#     'EMAIL': 'Email',
#     'EMAILDODINT': 'Email Day of Delivery Interactive',
#     'EMAIL_ATTEMPT': 'Email Attempted Delivery',
#     'EMAIL_COLL_REC': 'Email Collection Received',
#     'EMAIL_START_DEL': 'Email Start of Delivery',
#     'DELIVERY': 'Email Delivery',
#     'SMS_DOD': 'SMS Day of Despatch',
#     'SMS_START_DEL': 'SMS Start of Delivery',
#     'SMS_ATTEMPT_DEL': 'SMS Attempted Delivery',
#     'SMS_COLL_REC': 'SMS Collection Received',
# }


class CollectionNotificationType(str, Enum):
    EMAIL = 'EMAIL'
    EMAIL_RECIEVED = 'EMAILCOLLRECEIVED'
    SMS_RECIEVED = 'SMSCOLLRECEIVED'


