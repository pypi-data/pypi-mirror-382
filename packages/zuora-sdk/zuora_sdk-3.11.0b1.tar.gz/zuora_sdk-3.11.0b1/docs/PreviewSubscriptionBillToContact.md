# PreviewSubscriptionBillToContact

Container for bill-to contact information of this account. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**city** | **str** | The city of the bill-to address. The value should be 40 characters or less. | [optional] 
**country** | **str** | The country of the bill-to address. The value must be a valid country name or abbreviation.   **Note:** You must specify this field if you are using Zuora Tax for this account. | [optional] 
**county** | **str** | The county of the bill-to address. The value should be 32 characters or less. | [optional] 
**state** | **str** | The state of the bill-to address. The value must be a valid state or province name or 2-character abbreviation.   **Note:** You must specify this field if you are using Zuora Tax for this account and the country is &#x60;USA&#x60; or &#x60;Canada&#x60;. | [optional] 
**tax_region** | **str** | If using Zuora Tax, a region string as optionally defined in your tax rules. | [optional] 
**zip_code** | **str** | The zip code of the bill-to address. The value should be 20 characters or less. | [optional] 

## Example

```python
from zuora_sdk.models.preview_subscription_bill_to_contact import PreviewSubscriptionBillToContact

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewSubscriptionBillToContact from a JSON string
preview_subscription_bill_to_contact_instance = PreviewSubscriptionBillToContact.from_json(json)
# print the JSON string representation of the object
print(PreviewSubscriptionBillToContact.to_json())

# convert the object into a dict
preview_subscription_bill_to_contact_dict = preview_subscription_bill_to_contact_instance.to_dict()
# create an instance of PreviewSubscriptionBillToContact from a dict
preview_subscription_bill_to_contact_from_dict = PreviewSubscriptionBillToContact.from_dict(preview_subscription_bill_to_contact_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


