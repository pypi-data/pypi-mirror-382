# OrderCreateAccountContact

Contact details associated with an account. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**address1** | **str** | First line of the contact&#39;s address. This is often a street address or a business name. | [optional] 
**address2** | **str** | Second line of the contact&#39;s address.  | [optional] 
**city** | **str** | City of the contact&#39;s address.  | [optional] 
**contact_description** | **str** | A description for the contact.  | [optional] 
**country** | **str** | Country; must be a valid country name or abbreviation. If using Zuora Tax, you must specify a country in the bill-to contact to calculate tax. | [optional] 
**county** | **str** | County of the contact&#39;s address.  | [optional] 
**fax** | **str** | Fax number of the contact.  | [optional] 
**first_name** | **str** | First name of the contact.  | 
**home_phone** | **str** | Home phone number of the contact.  | [optional] 
**last_name** | **str** | Last name of the contact.  | 
**mobile_phone** | **str** | Mobile phone number of the contact.  | [optional] 
**nickname** | **str** | Nickname of the contact.  | [optional] 
**other_phone** | **str** | Additional phone number of the contact. Use the &#x60;otherPhoneType&#x60; field to specify the type of phone number. | [optional] 
**other_phone_type** | [**PhoneType**](PhoneType.md) |  | [optional] 
**personal_email** | **str** | Personal email address of the contact.  | [optional] 
**postal_code** | **str** | ZIP code or other postal code of the contact&#39;s address.  | [optional] 
**state** | **str** | State or province of the contact&#39;s address.  | [optional] 
**tax_region** | **str** | Region defined in your taxation rules. Only applicable if you use Zuora Tax. | [optional] 
**work_email** | **str** | Business email address of the contact.  | [optional] 
**work_phone** | **str** | Business phone number of the contact.  | [optional] 

## Example

```python
from zuora_sdk.models.order_create_account_contact import OrderCreateAccountContact

# TODO update the JSON string below
json = "{}"
# create an instance of OrderCreateAccountContact from a JSON string
order_create_account_contact_instance = OrderCreateAccountContact.from_json(json)
# print the JSON string representation of the object
print(OrderCreateAccountContact.to_json())

# convert the object into a dict
order_create_account_contact_dict = order_create_account_contact_instance.to_dict()
# create an instance of OrderCreateAccountContact from a dict
order_create_account_contact_from_dict = OrderCreateAccountContact.from_dict(order_create_account_contact_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


