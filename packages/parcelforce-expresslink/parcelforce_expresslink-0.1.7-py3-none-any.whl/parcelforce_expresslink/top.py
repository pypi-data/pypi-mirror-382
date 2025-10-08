import datetime as dt
import typing as _t

import pydantic

import parcelforce_expresslink.types
from parcelforce_expresslink.address import (
    AddTypes,
    AddressCollection,
    AddressRecipient,
    Contact,
    ContactCollection,
)
if _t.TYPE_CHECKING:
    from parcelforce_expresslink.shipment import Shipment

from parcelforce_expresslink.types import string_type
from parcelforce_expresslink.lists import (
    Barcodes,
    CompletedShipments,
    ContentDetails,
    HazardousGoods,
    Images,
    LabelData,
    ManifestShipments,
    NominatedDeliveryDatelist,
    ParcelContents,
    ServiceCodes,
    SpecifiedNeighbour,
)
from parcelforce_expresslink.models import DeliveryOptions, InBoundDetails
from parcelforce_expresslink.shared import DateTimeRange, Enhancement, PFBaseModel, Returns
from parcelforce_expresslink.services import ServiceCode


class PAF(PFBaseModel):
    postcode: str | None = None
    count: int | None = pydantic.Field(None)
    specified_neighbour: list[SpecifiedNeighbour] = pydantic.Field(
        default_factory=list, description=''
    )


class Department(PFBaseModel):
    department_id: list[int | None] = pydantic.Field(None, description='')
    service_codes: list[ServiceCodes | None] = pydantic.Field(None, description='')
    nominated_delivery_date_list: NominatedDeliveryDatelist | None = None


class Parcel(PFBaseModel):
    weight: float | None = None
    length: int | None = None
    height: int | None = None
    width: int | None = None
    purpose_of_shipment: str | None = None
    invoice_number: str | None = None
    export_license_number: str | None = None
    certificate_number: str | None = None
    content_details: ContentDetails | None = None
    shipping_cost: float | None = None


class ParcelLabelData(PFBaseModel):
    parcel_number: str | None = None
    shipment_number: str | None = None
    journey_leg: str | None = None
    label_data: LabelData | None = None
    barcodes: Barcodes | None = None
    images: Images | None = None
    parcel_contents: list[ParcelContents | None] = pydantic.Field(None, description='')


class CompletedManifestInfo(PFBaseModel):
    department_id: int
    manifest_number: str
    manifest_type: str
    total_shipment_count: int
    manifest_shipments: ManifestShipments


class CompletedShipmentInfoCreatePrint(PFBaseModel):
    lead_shipment_number: str | None = None
    shipment_number: str | None = None
    delivery_date: str | None = None
    status: str
    completed_shipments: CompletedShipments


class CompletedShipmentInfo(PFBaseModel):
    lead_shipment_number: str | None = None
    delivery_date: dt.date | None = None
    status: str | None = None
    completed_shipments: CompletedShipments | None = None


class CollectionInfo(PFBaseModel):
    collection_contact: ContactCollection
    collection_address: AddressCollection
    collection_time: DateTimeRange

    @classmethod
    def from_shipment(cls, shipment: 'Shipment') -> _t.Self:
        return cls(
            collection_address=AddressCollection(**shipment.recipient_address.model_dump()),
            collection_contact=ContactCollection.model_validate(
                shipment.recipient_contact.model_dump(exclude={'notifications'})
            ),
            collection_time=DateTimeRange.null_times_from_date(shipment.shipping_date),
        )


class CollectionStateProtocol(_t.Protocol):
    contact: Contact
    address: AddressCollection
    ship_date: dt.date


# def collection_info_from_state(state: CollectionStateProtocol):
#     col_contact_ = ContactCollection(**state.contact.model_dump(exclude={'notifications'}))
#     col_contact = col_contact_.model_validate(col_contact_)
#     info = CollectionInfo(
#         collection_contact=col_contact,
#         collection_address=state.address,
#         collection_time=DateTimeRange.from_datetimes(
#             dt.datetime.combine(state.ship_date, COLLECTION_TIME_FROM),
#             dt.datetime.combine(state.ship_date, COLLECTION_TIME_TO)
#         )
#     )
#     return info.model_validate(info)


class RequestedShipmentZero(PFBaseModel):
    recipient_contact: Contact
    recipient_address: AddTypes
    total_number_of_parcels: int = pydantic.Field(
        ..., description='Number of parcels in the shipment'
    )
    shipping_date: dt.date


class RequestedShipmentMinimum(RequestedShipmentZero):
    recipient_contact: Contact

    contract_number: str
    department_id: int = 1

    shipment_type: parcelforce_expresslink.types.ShipmentType = 'DELIVERY'
    service_code: ServiceCode = ServiceCode.EXPRESS24
    reference_number1: string_type(24) | None = None  # first 14 visible on label

    special_instructions1: pydantic.constr(max_length=25) | None = None
    special_instructions2: pydantic.constr(max_length=25) | None = None

    @pydantic.field_validator('reference_number1', mode='after')
    def ref_num_validator(cls, v, values):
        if not v:
            v = values.data.get('recipient_contact').delivery_contact_business
        return v


class CollectionMinimum(RequestedShipmentMinimum):
    shipment_type: parcelforce_expresslink.types.ShipmentType = 'COLLECTION'
    print_own_label: bool = True
    collection_info: CollectionInfo


class RequestedShipmentSimple(RequestedShipmentMinimum):
    enhancement: Enhancement | None = None
    delivery_options: DeliveryOptions | None = None


class Parcels(PFBaseModel):
    parcel: list[Parcel]


class ShipmentLabelData(PFBaseModel):
    parcel_label_data: list[ParcelLabelData]


class CompletedManifests(PFBaseModel):
    completed_manifest_info: list[CompletedManifestInfo]


class Departments(PFBaseModel):
    department: list[Department] = pydantic.Field(default_factory=list)


class NominatedDeliveryDates(PFBaseModel):
    service_code: str | None = None
    departments: Departments | None = None


class PostcodeExclusion(PFBaseModel):
    delivery_postcode: str | None = None
    collection_postcode: str | None = None
    departments: Departments | None = None


class InternationalInfo(PFBaseModel):
    parcels: Parcels | None = None
    exporter_customs_reference: str | None = None
    recipient_importer_vat_no: str | None = None
    original_export_shipment_no: str | None = None
    documents_only: bool | None = None
    documents_description: str | None = None
    value_under200_us_dollars: bool | None = None
    shipment_description: str | None = None
    comments: str | None = None
    invoice_date: str | None = None
    terms_of_delivery: str | None = None
    purchase_order_ref: str | None = None


class RequestedShipmentComplex(RequestedShipmentSimple):
    hazardous_goods: HazardousGoods | None = None
    consignment_handling: bool | None = None
    drop_off_ind: parcelforce_expresslink.types.DropOffInd | None = None
    exchange_instructions1: pydantic.constr(max_length=25) | None = None
    exchange_instructions2: pydantic.constr(max_length=25) | None = None
    exchange_instructions3: pydantic.constr(max_length=25) | None = None
    exporter_address: AddressRecipient | None = None
    exporter_contact: Contact | None = None
    importer_address: AddressRecipient | None = None
    importer_contact: Contact | None = None
    in_bound_address: AddressRecipient | None = None
    in_bound_contact: Contact | None = None
    in_bound_details: InBoundDetails | None = None
    international_info: InternationalInfo | None = None
    pre_printed: bool | None = None
    print_own_label: bool | None = None
    reference_number1: pydantic.constr(max_length=24) | None = None
    reference_number2: pydantic.constr(max_length=24) | None = None
    reference_number3: pydantic.constr(max_length=24) | None = None
    reference_number4: pydantic.constr(max_length=24) | None = None
    reference_number5: pydantic.constr(max_length=24) | None = None
    request_id: int | None = None
    returns: Returns | None = None
    special_instructions1: pydantic.constr(max_length=25) | None = None
    special_instructions2: pydantic.constr(max_length=25) | None = None
    special_instructions3: pydantic.constr(max_length=25) | None = None
    special_instructions4: pydantic.constr(max_length=25) | None = None

    # job_reference: str | None = None  # not required for domestic
    # sender_contact: Contact | None = None
    # sender_address: AddressSender | None = None
    # total_shipment_weight: float | None = None
    # enhancement: Enhancement | None = None
    # delivery_options: DeliveryOptions | None = None
