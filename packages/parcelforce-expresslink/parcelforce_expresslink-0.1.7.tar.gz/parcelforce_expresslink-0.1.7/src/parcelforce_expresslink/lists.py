import pydantic as _p
from .address import AddressTemporary
from .shared import (
    Barcode,
    CompletedCancelInfo,
    CompletedShipment,
    ContentData,
    ContentDetail,
    HazardousGood,
    Image,
    LabelItem,
    ManifestShipment,
    PFBaseModel,
)


class HazardousGoods(PFBaseModel):
    hazardous_good: list[HazardousGood]


class ContentDetails(PFBaseModel):
    content_detail: list[ContentDetail]


class ParcelContents(PFBaseModel):
    item: list[ContentData]


class LabelData(PFBaseModel):
    item: list[LabelItem]


class Barcodes(PFBaseModel):
    barcode: list[Barcode]


class Images(PFBaseModel):
    image: list[Image]


class ManifestShipments(PFBaseModel):
    manifest_shipment: list[ManifestShipment]


class CompletedShipments(PFBaseModel):
    completed_shipment: list[CompletedShipment] = _p.Field(default_factory=list)


class CompletedCancel(PFBaseModel):
    completed_cancel_info: CompletedCancelInfo | None = None


class NominatedDeliveryDatelist(PFBaseModel):
    nominated_delivery_date: list[str] = _p.Field(default_factory=list)


class SafePlacelist(PFBaseModel):
    safe_place: list[str] = _p.Field(default_factory=list)


class ServiceCodes(PFBaseModel):
    service_code: list[str] = _p.Field(default_factory=list)


class SpecifiedNeighbour(PFBaseModel):
    address: list[AddressTemporary] = _p.Field(default_factory=list)

    # @_p.field_validator('address', mode='after')
    # def check_add_type(cls, v, values):
    #     outaddrs = []
    #     for add in v:
    #         try:
    #             addr = pf_models.AddressRecipient.model_validate(add.model_dump(by_alias=True))
    #         except _p.ValidationError:
    #             addr = pf_models.AddressCollection.model_validate(add.model_dump(by_alias=True))
    #         outaddrs.append(addr)
    #     return outaddrs


#
# class SpecifiedNeighbour(PFBaseModel):
#     address: list[pf_models.AddressRecipient] = _p.Field(default_factory=list)
#
#     @_p.field_validator('address', mode='after')
#     def check_add_type(cls, v, values):
#         outaddrs = []
#         for add in v:
#             try:
#                 addr = pf_models.AddressRecipient.model_validate(add.model_dump(by_alias=True))
#             except _p.ValidationError:
#                 addr = pf_models.AddressCollection.model_validate(add.model_dump(by_alias=True))
#             outaddrs.append(addr)
#         return outaddrs
