# UpdateAccountContact

Container for bill-to/sold-to/ship-to contact information for this account. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**address1** | **str** | First address line, 255 characters or less.  | [optional] 
**address2** | **str** | Second address line, 255 characters or less.  | [optional] 
**city** | **str** | City, 40 characters or less.  | [optional] 
**country** | **str** | Country; must be a valid country name or abbreviation. If using Zuora Tax, you must specify a country in the sold-to contact to calculate tax. A bill-to contact may be used if no sold-to contact is provided. | [optional] 
**county** | **str** | County; 32 characters or less. May optionally be used by Zuora Tax to calculate county tax. | [optional] 
**fax** | **str** | Fax phone number, 40 characters or less.  | [optional] 
**first_name** | **str** | First name, 100 characters or less.  | 
**home_phone** | **str** | Home phone number, 40 characters or less.  | [optional] 
**last_name** | **str** | Last name, 100 characters or less.  | 
**mobile_phone** | **str** | Mobile phone number, 40 characters or less.  | [optional] 
**nickname** | **str** | Nickname for this contact  | [optional] 
**other_phone** | **str** | Other phone number, 40 characters or less.  | [optional] 
**other_phone_type** | [**PhoneType**](PhoneType.md) |  | [optional] 
**personal_email** | **str** | Personal email address, 80 characters or less.  | [optional] 
**state** | **str** | State; must be a valid state or province name or 2-character abbreviation. If using Zuora Tax, be aware that Zuora Tax requires a state (in the US) or province (in Canada) in this field for the sold-to contact to calculate tax, and that a bill-to contact may be used if no sold-to contact is provided. | [optional] 
**tax_region** | **str** | If using Zuora Tax, a region string as optionally defined in your tax rules. Not required. | [optional] 
**work_email** | **str** | Work email address, 80 characters or less.  | [optional] 
**work_phone** | **str** | Work phone number, 40 characters or less.  | [optional] 
**zip_code** | **str** | Zip code, 20 characters or less.  | [optional] 

## Example

```python
from zuora_sdk.models.update_account_contact import UpdateAccountContact

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateAccountContact from a JSON string
update_account_contact_instance = UpdateAccountContact.from_json(json)
# print the JSON string representation of the object
print(UpdateAccountContact.to_json())

# convert the object into a dict
update_account_contact_dict = update_account_contact_instance.to_dict()
# create an instance of UpdateAccountContact from a dict
update_account_contact_from_dict = UpdateAccountContact.from_dict(update_account_contact_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


