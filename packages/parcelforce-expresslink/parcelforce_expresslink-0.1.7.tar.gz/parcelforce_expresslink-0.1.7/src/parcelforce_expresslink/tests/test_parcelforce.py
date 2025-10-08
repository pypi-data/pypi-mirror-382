from parcelforce_expresslink.address import AddressRecipient, Contact
from parcelforce_expresslink.request_response import ShipmentResponse
from parcelforce_expresslink.shared import DateTimeRange
from parcelforce_expresslink.types import ShipmentType


def test_client_gets_candidates(sample_client, sample_address):
    addresses = sample_client.get_candidates(sample_address.postcode)
    assert isinstance(addresses, list)
    assert isinstance(addresses[0], AddressRecipient)
    assert addresses[0].postcode == sample_address.postcode


def check_label(sample_client, resp, tmp_path):
    label_data = sample_client.get_label_content(ship_num=resp.shipment_num)
    output = tmp_path / f'{resp.shipment_num}.pdf'
    output.write_bytes(label_data)
    assert output.exists()


def test_client_sends_outbound(sample_shipment, sample_client, tmp_path):
    resp = sample_client.request_shipment(sample_shipment)
    assert isinstance(resp, ShipmentResponse)
    assert not resp.alerts
    check_label(sample_client, resp, tmp_path)


def test_to_inbound(sample_shipment_inbound, sample_shipment, sample_contact):
    ...
    og_recipient_contact = sample_contact.model_dump(exclude={'notifications'})

    collection_info = sample_shipment_inbound.collection_info
    collection_contact = collection_info.collection_contact.model_dump(exclude={'notifications'})

    collection_contact_conveted_to_recipient = Contact.model_validate(
        collection_contact, from_attributes=True
    ).model_dump(exclude={'notifications'})


    assert og_recipient_contact == collection_contact_conveted_to_recipient
    assert sample_shipment_inbound.shipment_type == ShipmentType.COLLECTION
    assert sample_shipment_inbound.print_own_label == True
    assert collection_info.collection_address.model_dump() == sample_shipment.recipient_address.model_dump()
    assert collection_info.collection_time == DateTimeRange.null_times_from_date(sample_shipment.shipping_date)


def test_to_dropoff(sample_shipment_dropoff, sample_shipment):
    ...
    og_recipient_contact = sample_shipment.recipient_contact.model_dump(exclude={'notifications'})
    og_recipient_address = sample_shipment.recipient_address.model_dump()

    sender_contact = sample_shipment_dropoff.sender_contact.model_dump(exclude={'notifications'})
    sender_address = sample_shipment_dropoff.sender_address.model_dump()

    converted_back_recip = Contact.model_validate(sender_contact, from_attributes=True).model_dump(
        exclude={'notifications'}
    )
    assert og_recipient_contact == converted_back_recip
    assert og_recipient_address == sender_address
    assert sample_shipment_dropoff.shipment_type == ShipmentType.DELIVERY
    assert sample_shipment_dropoff.print_own_label is None
    assert sample_shipment_dropoff.collection_info is None


def test_client_sends_inbound(sample_shipment_inbound, sample_client, tmp_path):
    resp = sample_client.request_shipment(sample_shipment_inbound)
    assert isinstance(resp, ShipmentResponse)
    assert not resp.alerts
    check_label(sample_client, resp, tmp_path)


def test_client_sends_dropoff(sample_shipment_dropoff, sample_client, tmp_path):
    resp = sample_client.request_shipment(sample_shipment_dropoff)
    assert isinstance(resp, ShipmentResponse)
    assert not resp.alerts
    check_label(sample_client, resp, tmp_path)



