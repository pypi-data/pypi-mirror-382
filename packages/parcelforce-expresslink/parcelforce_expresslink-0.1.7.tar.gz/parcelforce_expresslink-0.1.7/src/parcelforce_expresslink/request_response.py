from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Self

import pydantic as pyd
from loguru import logger
from pydantic import Field, StringConstraints

from parcelforce_expresslink.config import ParcelforceSettings
from parcelforce_expresslink.types import ExpressLinkError
from parcelforce_expresslink.lists import CompletedCancel, SafePlacelist
from parcelforce_expresslink.models import (
    CompletedReturnInfo,
    ConvenientCollect,
    PostOffice,
    SpecifiedPostOffice,
)
from parcelforce_expresslink.shared import DateTimeRange, Document, PFBaseModel
from parcelforce_expresslink.shipment import Shipment
from parcelforce_expresslink.top import (
    CompletedManifests,
    CompletedShipmentInfo,
    CompletedShipmentInfoCreatePrint,
    NominatedDeliveryDates,
    PAF,
    PostcodeExclusion,
    RequestedShipmentMinimum,
    ShipmentLabelData,
)


class AlertType(StrEnum):
    ERROR = 'ERROR'
    WARNING = 'WARNING'
    NOTIFICATION = 'NOTIFICATION'


class Alert(PFBaseModel):
    code: int | None = None
    message: str
    type: AlertType = AlertType.NOTIFICATION


class Alerts(PFBaseModel):
    alert: list[Alert] = Field(default_factory=list[Alert])

    @classmethod
    def empty(cls):
        return cls(alert=[])


class Authentication(PFBaseModel):
    user_name: Annotated[str, StringConstraints(max_length=80)]
    password: Annotated[str, StringConstraints(max_length=80)]

    @classmethod
    def from_settings(cls, settings: ParcelforceSettings) -> Self:
        return cls(
            user_name=settings.pf_expr_usr.get_secret_value(),
            password=settings.pf_expr_pwd.get_secret_value(),
        )


class BaseRequest(PFBaseModel):
    authentication: Authentication | None = None

    def authenticated(self, auth):
        self.authentication = auth
        return self

    def authenticate(self, username: str, password: str):
        self.authentication = Authentication(user_name=username, password=password)
        return self

    def authenticate_from_settings(self):
        return self.authenticate(*ParcelforceSettings.from_env().get_auth_secrets())


class FindMessage(PFBaseModel):
    convenient_collect: ConvenientCollect | None = None
    specified_post_office: SpecifiedPostOffice | None = None
    paf: PAF | None = pyd.Field(None, alias='PAF')
    safe_places: bool | None = None
    nominated_delivery_dates: NominatedDeliveryDates | None = None
    postcode_exclusion: PostcodeExclusion | None = None


class FindRequest(FindMessage, BaseRequest): ...


class BaseResponse(PFBaseModel):
    alerts: Alerts | None = Field(default_factory=Alerts.empty)


class FindResponse(FindMessage, BaseResponse):
    safe_place_list: SafePlacelist | None = pyd.Field(default_factory=list)


class ShipmentRequest(BaseRequest):
    requested_shipment: Shipment


class ShipmentResponse(BaseResponse):
    completed_shipment_info: CompletedShipmentInfo | None = None

    @property
    def shipment_num(self):
        return (
            self.completed_shipment_info.completed_shipments.completed_shipment[0].shipment_number
            if self.completed_shipment_info
            else None
        )

    @property
    def status(self):
        if self.completed_shipment_info:
            return self.completed_shipment_info.status
        return 'No Completed Shipment Info'

    @property
    def success(self):
        if self.completed_shipment_info:
            return self.completed_shipment_info.status.lower() == 'allocated'
        return False

    def tracking_link(self):
        stem = ParcelforceSettings.from_env().tracking_url_stem
        tlink = f'{stem}PB{self.shipment_num}001'
        return tlink

    def handle_errors(self):
        if hasattr(self, 'Error'):  # Combadge adds this? or PF? not in WSDL but appears sometimes
            msg = self.Error.message if hasattr(self.Error, 'message') else str(self.Error)
            raise ExpressLinkError(msg)
        if hasattr(self, 'alerts') and hasattr(self.alerts, 'alert'):
            for _ in self.alerts.alert:
                match _.type:
                    case AlertType.ERROR:
                        logger.error('ExpressLinkl Error, booking failed?: ' + _.message)
                        raise ExpressLinkError(_.message)
                    case _:
                        logger.warning('Expresslink Warning: ' + _.message)


################################################################


class PrintType(StrEnum):
    ALL_PARCELS = 'ALL_PARCELS'
    SINGLE_PARCEL = 'SINGLE_PARCEL'


class PrintLabelRequest(BaseRequest):
    shipment_number: str
    print_format: str | None = None
    barcode_format: str | None = None
    print_type: PrintType = 'ALL_PARCELS'


class PrintLabelResponse(BaseResponse):
    label: Document | None = None
    label_data: ShipmentLabelData | None = None
    partner_code: str | None


################################################################


class PrintDocumentRequest(BaseRequest):
    shipment_number: str | None = None
    document_type: int | None = None
    print_format: str | None = None


class PrintDocumentResponse(BaseResponse):
    label: Document | None = None
    label_data: ShipmentLabelData | None = None
    document_type: Document | None = None


################################################################


class CreateManifestRequest(BaseRequest):
    department_id: int | None = None


class CreateManifestResponse(BaseResponse):
    completed_manifests: CompletedManifests | None = None


################################################################


class PrintManifestRequest(BaseRequest):
    manifest_number: str
    print_format: str | None = None


class PrintManifestResponse(BaseResponse):
    manifest: Document | None = None


################################################################


class ReturnShipmentRequest(BaseRequest):
    shipment_number: str
    collection_time: DateTimeRange | None = None


class ReturnShipmentResponse(BaseResponse):
    completed_shipment_info: CompletedReturnInfo | None = None


################################################################


class CCReserveRequest(BaseRequest):
    booking_reference: str


class CCReserveResponse(BaseResponse):
    post_office: PostOffice | None = None


################################################################


class CancelShipmentRequest(BaseRequest):
    shipment_number: str


class CancelShipmentResponse(BaseResponse):
    completed_cancel: CompletedCancel | None = pyd.Field(default_factory=list)


################################################################


class CreatePrintRequest(BaseRequest):
    requested_shipment: RequestedShipmentMinimum


class CreatePrintResponse(BaseResponse):
    completed_shipment_info_create_print: CompletedShipmentInfoCreatePrint | None = None
    label: Document | None = None
    label_data: ShipmentLabelData | None = None
    partner_code: str | None

################################################################
