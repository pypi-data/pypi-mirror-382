# Installation

pip install parcelforce-expresslink

# Setup

## Env File

(auto-read from os.environ['PARCELFORCE_ENV'])

### required

PF_AC_NUM_1  
PF_CONTRACT_NUM_1  
PF_EXPR_USR  
PF_EXPR_PWD

### optional

PF_ENDPOINT = "https://expresslink.parcelforce.net/ws"  
PF_WSDL = (bundled)  
PF_BINDING ="{http://www.parcelforce.net/ws/ship/v14}ShipServiceSoapBinding"  
tracking_url_stem = https://www.royalmail.com/track-your-item#/tracking-results/"  

# Usage
``` python
   recip_address = AddressRecipient(
        address_line1="An AddressLine",
        town="A Town",
        postcode="AA1BB2",
    )
    recip_contact = Contact(
        contact_name="A Name",
        email_address="anaddress@adomain.com",
        mobile_phone="07123456789",
        business_name="A Business Name",
    )
    shipment = Shipment(
        recipient_address=recip_address,
        recipient_contact=recip_contact,
        total_number_of_parcels=1,
        shipping_date=date.today(),
    )
    client = ParcelforceClient()
    response: ShipmentResponse = client.request_shipment(shipment)
    print(f"Shipment Number: {response.shipment_num}, Status: {response.status}")
```