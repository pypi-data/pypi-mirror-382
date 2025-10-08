from __future__ import annotations

from functools import lru_cache
from typing import Self

import pydantic
import zeep
from combadge.core.typevars import ServiceProtocolT
from combadge.support.zeep.backends.sync import ZeepBackend
from loguru import logger
from pydantic import model_validator
from thefuzz import fuzz, process
from zeep.proxy import ServiceProxy

from parcelforce_expresslink.combadge import (
    CancelShipmentService,
    CreateManifestService,
    CreateShipmentService,
    FindService,
    PrintLabelService,
)
from parcelforce_expresslink.address import AddTypes, AddressChoice, AddressRecipient
from parcelforce_expresslink.request_response import (
    Authentication,
    CancelShipmentRequest,
    CancelShipmentResponse,
    CreateManifestRequest,
    CreateManifestResponse,
    FindRequest,
    PrintLabelRequest,
    PrintLabelResponse,
    ShipmentRequest,
    ShipmentResponse,
    BaseRequest,
)
from parcelforce_expresslink.config import ParcelforceSettings
from parcelforce_expresslink.shipment import Shipment
from parcelforce_expresslink.top import PAF
from parcelforce_expresslink.types import VALID_POSTCODE

SCORER = fuzz.token_sort_ratio


# @functools.lru_cache(maxsize=1)
class ParcelforceClient(pydantic.BaseModel):
    """Client for Parcelforce ExpressLink API.

    Attributes:
        settings: pf_config.PFSettings - settings for the client
        service: ServiceProxy | None - Zeep ServiceProxy (generated from settings)
    """

    settings: ParcelforceSettings
    service: ServiceProxy | None = None
    strict: bool = True

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True, validate_default=True)

    def authenticate_request(self, req: BaseRequest):
        req.authentication = Authentication.from_settings(self.settings)

    @classmethod
    @lru_cache
    def from_env(cls, env_name='PARCELFORCE_ENV') -> Self:
        return cls(settings=ParcelforceSettings.from_env(env_name))

    @model_validator(mode='after')
    def get_service(self):
        if self.service is None:
            self.service = self.new_service()
        return self

    def new_service(self) -> zeep.proxy.ServiceProxy:
        client = zeep.Client(
            wsdl=self.settings.pf_wsdl,
            settings=zeep.settings.Settings(strict=self.strict),
        )
        return client.create_service(
            binding_name=self.settings.pf_binding, address=self.settings.pf_endpoint
        )

    def backend(self, service_prot: type[ServiceProtocolT]) -> zeep.proxy.ServiceProxy:
        """Get a Combadge backend for a service_code protocol.

        Args:
            service_prot: type[ServiceProtocolT] - service_code protocol to get backend for

        Returns:
            ServiceProxy - Zeep Proxy

        """
        return ZeepBackend(self.service)[service_prot]

    def request_shipment(self, shipment: Shipment) -> ShipmentResponse:
        """Submit a ShipmentRequest to Parcelforce, booking carriage.

        Args:
            shipment: Shipment - ShipmenmtRequest to book

        Returns:
            .ShipmentResponse - response from Parcelforce

        """
        back = self.backend(CreateShipmentService)
        shipment_request = ShipmentRequest(requested_shipment=shipment)
        self.authenticate_request(shipment_request)
        resp: ShipmentResponse = back.createshipment(
            request=shipment_request.model_dump(by_alias=True)
        )
        resp.handle_errors()
        return resp

    def cancel_shipment(self, shipment_number):
        req = CancelShipmentRequest(shipment_number=shipment_number).authenticate_from_settings()
        back = self.backend(CancelShipmentService)
        response: CancelShipmentResponse = back.cancelshipment(
            request=req.model_dump(by_alias=True)
        )
        return response

    def get_candidates(self, postcode: str) -> list[AddressRecipient]:
        """Get candidate addresses at a postcode.

        Args:
            postcode: str - postcode to search for

        Returns:
            list[.models.AddressRecipient] - list of candidate addresses

        """
        postcode = clean_up_postcode(postcode)
        req = FindRequest(paf=PAF(postcode=postcode))
        self.authenticate_request(req)
        back = self.backend(FindService)
        response = back.find(request=req.model_dump(by_alias=True))
        if not response.paf:
            logger.info(f'No candidates found for {postcode}')
            return []
        return [neighbour.address[0] for neighbour in response.paf.specified_neighbour]

    def get_label_content(
        self, ship_num, print_format: str | None = None, barcode_format: str | None = None
    ) -> bytes:
        response = self.get_label_response(ship_num, barcode_format, print_format)
        return response.label.data

    def get_label_response(
        self, ship_num: str, barcode_format: str | None = None, print_format: str | None = None
    ):
        back = self.backend(PrintLabelService)
        # req = PrintLabelRequest(authentication=self.settings.auth(), shipment_number=ship_num)
        req = PrintLabelRequest(
            authentication=Authentication.from_settings(self.settings),
            shipment_number=ship_num,
            print_format=print_format,
            barcode_format=barcode_format,
        )
        response: PrintLabelResponse = back.printlabel(request=req)
        if response.alerts:
            for alt in response.alerts.alert:
                if alt.type == 'ERROR':
                    raise ValueError(f'ExpressLink Error: {alt.message}')
                logger.warning(f'ExpressLink Warning: {alt.message}')
        return response

    # def get_label(
    #     self, ship_num, dl_path: str, print_format: str | None = None, barcode_format: str | None = None
    # ) -> Path:
    #     """Get the label for a shipment number.
    #
    #     Args:
    #         ship_num: str - shipment number
    #         dl_path: str - path to download the label to, defaults to './temp_label.pdf'
    #         print_format: str | None (default = PDF)
    #         PDF - to return a PDF image of the Label.
    #         XML - to return a data stream in order to create own label.
    #         PDF-XML - to return the Parcelforce label as PDF and the Partner label as XML.
    #         XML-PDF – to return the Parcelforce label as XML and the Partner label as PDF
    #
    #         barcode_format: Set to PNG to return image of Barcode in Base64 code
    #
    #     Returns:
    #         Path - path to the downloaded label
    #
    #     """
    #     response = self.get_label_response(ship_num, barcode_format, print_format)
    #
    #     out_path = response.label.download(Path(dl_path))
    #     logger.info(f'Downloaded label to {out_path}')
    #     return out_path

    def get_manifest(self):
        back = self.backend(CreateManifestService)
        req = CreateManifestRequest(authentication=Authentication.from_settings())
        response: CreateManifestResponse = back.createmanifest(request=req)
        return response

    def choose_address[T: AddTypes](self, address: T) -> tuple[T, int]:
        """Takes a potentially invalid address, and returns the closest match from ExpressLink with fuzzy score."""
        candidates = self.get_candidates(address.postcode)
        candidate_strs = [c.lines_str for c in candidates]
        chosen, score = process.extractOne(address.lines_str, candidate_strs, scorer=SCORER)
        chosen_add = candidates[candidate_strs.index(chosen)]
        return chosen_add, score

    def address_choice[T: AddTypes](self, address: T) -> AddressChoice:
        logger.info(f'Choosing address for {address.lines_str} @ {address.postcode}')
        chosen, score = self.choose_address(address)
        return AddressChoice(address=chosen, score=score)

    def get_choices[T: AddTypes](
        self, postcode: VALID_POSTCODE, address: T | None = None
    ) -> list[AddressChoice]:
        candidates = self.get_candidates(postcode)
        if not address:
            return [AddressChoice(address=add, score=0) for add in candidates]
        candidate_dict = {add.lines_str: add for add in candidates}
        scored = process.extract(
            address.lines_str,
            candidate_dict.keys(),
            scorer=SCORER,
            limit=None,
        )
        choices = [AddressChoice(address=candidate_dict[add], score=score) for add, score in scored]
        return sorted(
            choices,
            key=lambda x: x.score,
            reverse=True,
        )

    # def get_choices_agnost(self, postcode: VALID_POSTCODE, address: AddressAgnost | None = None) -> list[AddressChoice]:
    #     candidates = self.get_candidates_agnost(postcode)
    #     if not address:
    #         return [AddressChoice(address=add, score=0) for add in candidates]
    #     candidate_dict = {add.lines_str: add for add in candidates}
    #     scored = process.extract(
    #         address.lines_str,
    #         candidate_dict.keys(),
    #         scorer=SCORER,
    #         limit=None,
    #     )
    #     choices = [AddressChoice(address=candidate_dict[add], score=score) for add, score in scored]
    #     return sorted(
    #         choices,
    #         key=lambda x: x.score,
    #         reverse=True,
    #     )

    def candidates_json(self, postcode):
        return {add.lines_str: add.model_dump_json() for add in self.get_candidates(postcode)}


def clean_up_postcode(postcode: str):
    postcode = postcode.upper()
    return postcode


#
# def wait_label(shipment_num, dl_path: str, el_client: ParcelforceClient) -> Path:
#     label_path = el_client.get_label(ship_num=shipment_num, dl_path=dl_path).resolve()
#     for i in range(20):
#         if label_path:
#             return label_path
#         else:
#             print('waiting for file to be created')
#             time.sleep(1)
#     else:
#         raise ValueError(f'file not created after 20 seconds {label_path=}')


