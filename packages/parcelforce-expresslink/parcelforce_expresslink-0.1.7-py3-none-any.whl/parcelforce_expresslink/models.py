from .shared import DateTimeRange, Enhancement, OpeningHours, PFBaseModel, Position

from .address import AddressRecipient


class PostOffice(PFBaseModel):
    post_office_id: str | None = None
    business: str | None = None
    address: AddressRecipient | None = None
    opening_hours: OpeningHours | None = None
    distance: float | None = None
    availability: bool | None = None
    position: Position | None = None
    booking_reference: str | None = None


class ConvenientCollect(PFBaseModel):
    postcode: str | None = None
    post_office: list[PostOffice] | None = None
    count: int | None = None
    post_office_id: str | None = None


class SpecifiedPostOffice(PFBaseModel):
    postcode: str | None = None
    post_office: list[PostOffice | None]
    count: int | None = None
    post_office_id: str | None = None


class CompletedReturnInfo(PFBaseModel):
    status: str
    shipment_number: str
    collection_time: DateTimeRange


class InBoundDetails(PFBaseModel):
    contract_number: str
    service_code: str
    total_shipment_weight: str | None = None
    enhancement: Enhancement | None = None
    reference_number1: str | None = None
    reference_number2: str | None = None
    reference_number3: str | None = None
    reference_number4: str | None = None
    reference_number5: str | None = None
    special_instructions1: str | None = None
    special_instructions2: str | None = None
    special_instructions3: str | None = None
    special_instructions4: str | None = None


class DeliveryOptions(PFBaseModel):
    convenient_collect: ConvenientCollect | None = None
    irts: bool | None = None
    letterbox: bool | None = None
    specified_post_office: SpecifiedPostOffice | None = None
    specified_neighbour: str | None = None
    safe_place: str | None = None
    pin: int | None = None
    named_recipient: bool | None = None
    address_only: bool | None = None
    nominated_delivery_date: str | None = None
    personal_parcel: str | None = None
