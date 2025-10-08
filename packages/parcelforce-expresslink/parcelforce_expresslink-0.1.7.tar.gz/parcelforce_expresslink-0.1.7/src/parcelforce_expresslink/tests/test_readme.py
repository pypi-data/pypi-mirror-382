from datetime import date

from parcelforce_expresslink.client import ParcelforceClient
from parcelforce_expresslink.address import AddressRecipient, Contact
from parcelforce_expresslink.request_response import ShipmentResponse
from parcelforce_expresslink.shipment import Shipment


def test_readme(sample_settings):
    recip_address = AddressRecipient(
        address_line1='Broadcasting House',
        town='London',
        postcode='W1A 1AA',
    )
    recip_contact = Contact(
        contact_name='A Name',
        email_address='anaddress@adomain.com',
        mobile_phone='07123456789',
        business_name='The BBC',
    )
    shipment = Shipment(
        recipient_address=recip_address,
        recipient_contact=recip_contact,
        total_number_of_parcels=1,
        shipping_date=date.today(),
        contract_number=sample_settings.pf_contract_num_1,
    )
    client = ParcelforceClient.from_env()
    response: ShipmentResponse = client.request_shipment(shipment)
    assert response.shipment_num is not None




