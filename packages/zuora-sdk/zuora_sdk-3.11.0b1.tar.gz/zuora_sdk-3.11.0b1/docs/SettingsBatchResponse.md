# SettingsBatchResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**responses** | [**List[SettingValueResponseWrapper]**](SettingValueResponseWrapper.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.settings_batch_response import SettingsBatchResponse

# TODO update the JSON string below
json = "{}"
# create an instance of SettingsBatchResponse from a JSON string
settings_batch_response_instance = SettingsBatchResponse.from_json(json)
# print the JSON string representation of the object
print(SettingsBatchResponse.to_json())

# convert the object into a dict
settings_batch_response_dict = settings_batch_response_instance.to_dict()
# create an instance of SettingsBatchResponse from a dict
settings_batch_response_from_dict = SettingsBatchResponse.from_dict(settings_batch_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


