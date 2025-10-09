# GetUsagesByAccountResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** | URL to retrieve the next page of the response if it exists; otherwise absent. | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 
**usage** | [**List[UsageItem]**](UsageItem.md) | Contains one or more usage items.  | [optional] 

## Example

```python
from zuora_sdk.models.get_usages_by_account_response import GetUsagesByAccountResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetUsagesByAccountResponse from a JSON string
get_usages_by_account_response_instance = GetUsagesByAccountResponse.from_json(json)
# print the JSON string representation of the object
print(GetUsagesByAccountResponse.to_json())

# convert the object into a dict
get_usages_by_account_response_dict = get_usages_by_account_response_instance.to_dict()
# create an instance of GetUsagesByAccountResponse from a dict
get_usages_by_account_response_from_dict = GetUsagesByAccountResponse.from_dict(get_usages_by_account_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


