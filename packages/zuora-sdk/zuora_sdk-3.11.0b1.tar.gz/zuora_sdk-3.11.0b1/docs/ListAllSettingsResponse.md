# ListAllSettingsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**settings** | [**List[SettingItemWithOperationsInformation]**](SettingItemWithOperationsInformation.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.list_all_settings_response import ListAllSettingsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ListAllSettingsResponse from a JSON string
list_all_settings_response_instance = ListAllSettingsResponse.from_json(json)
# print the JSON string representation of the object
print(ListAllSettingsResponse.to_json())

# convert the object into a dict
list_all_settings_response_dict = list_all_settings_response_instance.to_dict()
# create an instance of ListAllSettingsResponse from a dict
list_all_settings_response_from_dict = ListAllSettingsResponse.from_dict(list_all_settings_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


