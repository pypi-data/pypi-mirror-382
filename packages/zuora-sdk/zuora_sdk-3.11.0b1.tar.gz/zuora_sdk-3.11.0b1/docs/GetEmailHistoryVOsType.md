# GetEmailHistoryVOsType


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**email_histories** | [**List[GetEmailHistoryVOType]**](GetEmailHistoryVOType.md) | A container for email histories.  | [optional] 
**next_page** | **str** | URL to retrieve the next page of the response if it exists; otherwise absent. | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 

## Example

```python
from zuora_sdk.models.get_email_history_vos_type import GetEmailHistoryVOsType

# TODO update the JSON string below
json = "{}"
# create an instance of GetEmailHistoryVOsType from a JSON string
get_email_history_vos_type_instance = GetEmailHistoryVOsType.from_json(json)
# print the JSON string representation of the object
print(GetEmailHistoryVOsType.to_json())

# convert the object into a dict
get_email_history_vos_type_dict = get_email_history_vos_type_instance.to_dict()
# create an instance of GetEmailHistoryVOsType from a dict
get_email_history_vos_type_from_dict = GetEmailHistoryVOsType.from_dict(get_email_history_vos_type_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


