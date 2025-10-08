from __future__ import annotations

from typing import Annotated, Protocol

from combadge.core.interfaces import SupportsService
from combadge.support.http.markers import Payload
from combadge.support.soap.markers import operation_name

from parcelforce_expresslink import request_response


class FindService(SupportsService, Protocol):
    @operation_name('Find')
    def find(self, request: Annotated[request_response.FindRequest, Payload(by_alias=True)]) -> request_response.FindResponse:
        ...


class CreateShipmentService(SupportsService, Protocol):
    @operation_name('createShipment')
    def createshipment(
            self,
            request: Annotated[request_response.ShipmentRequest, Payload(by_alias=True)],
    ) -> request_response.ShipmentResponse:
        ...


class CCReserveService(SupportsService, Protocol):
    @operation_name('CCReserve')
    def ccreserve(
            self,
            request: Annotated[request_response.CCReserveRequest, Payload(by_alias=True)],
    ) -> request_response.CCReserveResponse:
        ...


class CancelShipmentService(SupportsService, Protocol):
    @operation_name('CancelShipment')
    def cancelshipment(
            self,
            request: Annotated[request_response.CancelShipmentRequest, Payload(by_alias=True)],
    ) -> request_response.CancelShipmentResponse:
        ...


class PrintManifestService(SupportsService, Protocol):
    @operation_name('printManifest')
    def printmanifest(
            self,
            request: Annotated[request_response.PrintManifestRequest, Payload(by_alias=True)],
    ) -> request_response.PrintManifestResponse:
        ...


class CreateManifestService(SupportsService, Protocol):
    @operation_name('createManifest')
    def createmanifest(
            self,
            request: Annotated[request_response.CreateManifestRequest, Payload(by_alias=True)],
    ) -> request_response.CreateManifestResponse:
        ...


class PrintDocumentService(SupportsService, Protocol):
    @operation_name('printDocument')
    def printdocument(
            self,
            request: Annotated[request_response.PrintDocumentRequest, Payload(by_alias=True)],
    ) -> request_response.PrintDocumentResponse:
        ...


class ReturnShipmentService(SupportsService, Protocol):
    @operation_name('returnShipment')
    def returnshipment(
            self,
            request: Annotated[request_response.ReturnShipmentRequest, Payload(by_alias=True)],
    ) -> request_response.ReturnShipmentResponse:
        ...


class PrintLabelService(SupportsService, Protocol):
    @operation_name('printLabel')
    def printlabel(
            self,
            request: Annotated[request_response.PrintLabelRequest, Payload(by_alias=True)],
    ) -> request_response.PrintLabelResponse:
        ...
