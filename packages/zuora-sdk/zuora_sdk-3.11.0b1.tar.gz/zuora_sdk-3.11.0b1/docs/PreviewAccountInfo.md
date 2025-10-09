# PreviewAccountInfo

Information about the account that will own the order. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**bill_cycle_day** | **int** | Day of the month that the account prefers billing periods to begin on. If set to 0, the bill cycle day will be set as \&quot;AutoSet\&quot;. | 
**currency** | **str** | ISO 3-letter currency code (uppercase). For example, USD.  | 
**custom_fields** | **Dict[str, object]** | Container for custom fields of an Account object.  | [optional] 
**sold_to_contact** | [**PreviewContactInfo**](PreviewContactInfo.md) |  | [optional] 
**ship_to_contact** | [**PreviewContactInfo**](PreviewContactInfo.md) |  | [optional] 
**tax_info** | [**TaxInfo**](TaxInfo.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.preview_account_info import PreviewAccountInfo

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewAccountInfo from a JSON string
preview_account_info_instance = PreviewAccountInfo.from_json(json)
# print the JSON string representation of the object
print(PreviewAccountInfo.to_json())

# convert the object into a dict
preview_account_info_dict = preview_account_info_instance.to_dict()
# create an instance of PreviewAccountInfo from a dict
preview_account_info_from_dict = PreviewAccountInfo.from_dict(preview_account_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


