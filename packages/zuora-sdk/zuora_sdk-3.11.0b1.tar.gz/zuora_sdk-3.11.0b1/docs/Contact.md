# Contact

Container for response about the contact. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the contact.  | [optional] 
**account_id** | **str** | The ID of the account associated with the contact.  | [optional] 
**account_number** | **str** | The number of the customer account associated with the contact.  | [optional] 
**address1** | **str** | The first line of the contact&#39;s address, which is often a street address or business name. | [optional] 
**address2** | **str** | The second line of the contact&#39;s address.  | [optional] 
**city** | **str** | The city of the contact&#39;s address.  | [optional] 
**contact_description** | **str** | A description for the contact.  | [optional] 
**country** | **str** | The country of the contact&#39;s address.  | [optional] 
**county** | **str** | The county. May optionally be used by Zuora Tax to calculate county tax. | [optional] 
**fax** | **str** | The contact&#39;s fax number.  | [optional] 
**first_name** | **str** | The contact&#39;s first name.  | [optional] 
**home_phone** | **str** | The contact&#39;s home phone number.  | [optional] 
**last_name** | **str** | The contact&#39;s last name.  | [optional] 
**mobile_phone** | **str** | The mobile phone number of the contact.  | [optional] 
**nickname** | **str** | A nickname for the contact.  | [optional] 
**other_phone** | **str** | An additional phone number for the contact.  | [optional] 
**other_phone_type** | [**PhoneType**](PhoneType.md) |  | [optional] 
**personal_email** | **str** | The contact&#39;s personal email address.  | [optional] 
**state** | **str** | The state or province of the contact&#39;s address.  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 
**tax_region** | **str** | If using Zuora Tax, a region string as optionally defined in your tax rules. Not required. | [optional] 
**work_email** | **str** | The contact&#39;s business email address.  | [optional] 
**work_phone** | **str** | The contact&#39;s business phone number.  | [optional] 
**zip_code** | **str** | The zip code for the contact&#39;s address.  | [optional] 
**postal_code** | **str** | Same as zipCode, used in get subscription billto, soldto contact info.  | [optional] 
**as_bill_to** | **bool** | Indicates the contact can as a bill to. Need Permission &#39;ShipToContactSupport&#39;  | [optional] 
**as_sold_to** | **bool** | Indicates the contact can as a sold to. Need Permission &#39;ShipToContactSupport&#39;  | [optional] 
**as_ship_to** | **bool** | Indicates the contact can as a ship to. Need Permission &#39;ShipToContactSupport&#39;  | [optional] 

## Example

```python
from zuora_sdk.models.contact import Contact

# TODO update the JSON string below
json = "{}"
# create an instance of Contact from a JSON string
contact_instance = Contact.from_json(json)
# print the JSON string representation of the object
print(Contact.to_json())

# convert the object into a dict
contact_dict = contact_instance.to_dict()
# create an instance of Contact from a dict
contact_from_dict = Contact.from_dict(contact_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


