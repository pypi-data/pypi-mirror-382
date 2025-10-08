import os

os.environ['PARCELFORCE_ENV'] = r'C:\prdev\envs\amdev\sandbox\parcelforce.env'
import sys
from datetime import date, timedelta

import pytest

from parcelforce_expresslink.config import ParcelforceSettings
from parcelforce_expresslink.client import ParcelforceClient
from parcelforce_expresslink.address import AddressRecipient, Contact
from parcelforce_expresslink.shipment import Shipment

TEST_DATE = date.today() + timedelta(days=2)
if TEST_DATE.weekday() in (5, 6):
    TEST_DATE += timedelta(days=7 - TEST_DATE.weekday())


@pytest.fixture(autouse=True)
def sandbox_only():
    settings = ParcelforceSettings.from_env()
    if 'test' not in settings.pf_endpoint:
        pytest.skip('Skipping ParcelForce tests outside sandbox environment')
        sys.exit()


@pytest.fixture
def sample_settings():
    settings = ParcelforceSettings.from_env()
    assert 'test' in settings.pf_endpoint.lower(), 'Not using test endpoint!'
    return settings


@pytest.fixture
def sample_address():
    return AddressRecipient(
        address_line1='Broadcasting House',
        town='London',
        postcode='W1A 1AA',
    )


@pytest.fixture
def sample_contact():
    return Contact(
        contact_name='A Name',
        email_address='anaddress@adomain.com',
        mobile_phone='07123456789',
        business_name='The BBC',
    )


@pytest.fixture
def sample_shipment(sample_settings, sample_address, sample_contact):
    return Shipment(
        recipient_address=sample_address,
        recipient_contact=sample_contact,
        total_number_of_parcels=1,
        shipping_date=TEST_DATE,
        contract_number=sample_settings.pf_contract_num_1,
    )


@pytest.fixture
def sample_shipment_dropoff(sample_shipment, sample_home_address, sample_home_contact):
    return sample_shipment.swap_sender_recipient(
        recipient_address=sample_home_address,
        recipient_contact=sample_home_contact,
    )


@pytest.fixture
def sample_shipment_inbound(sample_shipment_dropoff, sample_home_address, sample_home_contact):
    sample_shipment_dropoff.print_own_label = True
    return sample_shipment_dropoff.change_sender_to_collection()


@pytest.fixture
def sample_client() -> ParcelforceClient:
    client = ParcelforceClient.from_env()
    return client


@pytest.fixture
def sample_home_address():
    return AddressRecipient(
        address_line1='Home Address',
        town='Home Town',
        postcode='HA1 1AA',
    )


@pytest.fixture
def sample_home_contact():
    return Contact(
        contact_name='Home Name',
        business_name='Home Business',
        email_address='fake@nmo.com',
        mobile_phone='07123456789',
    )
