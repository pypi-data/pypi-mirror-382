# SettingsBatchRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**requests** | [**List[SettingValueRequest]**](SettingValueRequest.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.settings_batch_request import SettingsBatchRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SettingsBatchRequest from a JSON string
settings_batch_request_instance = SettingsBatchRequest.from_json(json)
# print the JSON string representation of the object
print(SettingsBatchRequest.to_json())

# convert the object into a dict
settings_batch_request_dict = settings_batch_request_instance.to_dict()
# create an instance of SettingsBatchRequest from a dict
settings_batch_request_from_dict = SettingsBatchRequest.from_dict(settings_batch_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


