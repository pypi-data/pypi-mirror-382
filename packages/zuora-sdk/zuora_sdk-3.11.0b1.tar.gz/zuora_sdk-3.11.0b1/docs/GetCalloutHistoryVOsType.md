# GetCalloutHistoryVOsType


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**callout_histories** | [**List[GetCalloutHistoryVOType]**](GetCalloutHistoryVOType.md) | A container for callout histories.  | [optional] 
**next_page** | **str** | URL to retrieve the next page of the response if it exists; otherwise absent. | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 

## Example

```python
from zuora_sdk.models.get_callout_history_vos_type import GetCalloutHistoryVOsType

# TODO update the JSON string below
json = "{}"
# create an instance of GetCalloutHistoryVOsType from a JSON string
get_callout_history_vos_type_instance = GetCalloutHistoryVOsType.from_json(json)
# print the JSON string representation of the object
print(GetCalloutHistoryVOsType.to_json())

# convert the object into a dict
get_callout_history_vos_type_dict = get_callout_history_vos_type_instance.to_dict()
# create an instance of GetCalloutHistoryVOsType from a dict
get_callout_history_vos_type_from_dict = GetCalloutHistoryVOsType.from_dict(get_callout_history_vos_type_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


