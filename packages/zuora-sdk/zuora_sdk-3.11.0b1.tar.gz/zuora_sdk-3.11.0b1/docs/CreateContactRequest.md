# CreateContactRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_id** | **str** | The ID of the account associated with the contact.    **Note**: When creating a contact, you must specify &#x60;accountNumber&#x60;, &#x60;accountId&#x60;, or both in the request body. If both fields are specified, they must correspond to the same account. | [optional] 
**account_number** | **str** | The number of the customer account associated with the contact.    **Note**: When creating a contact, you must specify &#x60;accountNumber&#x60;, &#x60;accountId&#x60;, or both in the request body. If both fields are specified, they must correspond to the same account. | [optional] 
**address1** | **str** | The first line of the contact&#39;s address, which is often a street address or business name. | [optional] 
**address2** | **str** | The second line of the contact&#39;s address.  | [optional] 
**city** | **str** | The city of the contact&#39;s address.  | [optional] 
**contact_description** | **str** | A description for the contact.  | [optional] 
**country** | **str** | The country of the contact&#39;s address.  | [optional] 
**county** | **str** | The county. May optionally be used by Zuora Tax to calculate county tax. | [optional] 
**fax** | **str** | The contact&#39;s fax number.  | [optional] 
**first_name** | **str** | The contact&#39;s first name.  | 
**home_phone** | **str** | The contact&#39;s home phone number.  | [optional] 
**last_name** | **str** | The contact&#39;s last name.  | 
**mobile_phone** | **str** | The mobile phone number of the contact.  | [optional] 
**nickname** | **str** | A nickname for the contact.  | [optional] 
**other_phone** | **str** | An additional phone number for the contact.  | [optional] 
**other_phone_type** | [**PhoneType**](PhoneType.md) |  | [optional] 
**personal_email** | **str** | The contact&#39;s personal email address.  | [optional] 
**state** | **str** | The state or province of the contact&#39;s address.  | [optional] 
**tax_region** | **str** | If using Zuora Tax, a region string as optionally defined in your tax rules. Not required. | [optional] 
**work_email** | **str** | The contact&#39;s business email address.  | [optional] 
**work_phone** | **str** | The contact&#39;s business phone number.  | [optional] 
**zip_code** | **str** | The zip code for the contact&#39;s address.  | [optional] 
**as_bill_to** | **bool** | Mark the contact as a bill to. Need Permission &#39;ShipToContactSupport&#39;  | [optional] 
**as_sold_to** | **bool** | Mark the contact as a sold to. Need Permission &#39;ShipToContactSupport&#39;  | [optional] 
**as_ship_to** | **bool** | Mark the contact as a ship to. Need Permission &#39;ShipToContactSupport&#39;  | [optional] 

## Example

```python
from zuora_sdk.models.create_contact_request import CreateContactRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateContactRequest from a JSON string
create_contact_request_instance = CreateContactRequest.from_json(json)
# print the JSON string representation of the object
print(CreateContactRequest.to_json())

# convert the object into a dict
create_contact_request_dict = create_contact_request_instance.to_dict()
# create an instance of CreateContactRequest from a dict
create_contact_request_from_dict = CreateContactRequest.from_dict(create_contact_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


