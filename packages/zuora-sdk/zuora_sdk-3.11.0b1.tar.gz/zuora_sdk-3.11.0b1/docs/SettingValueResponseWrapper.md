# SettingValueResponseWrapper


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The Id of the corresponding request.  | [optional] 
**method** | [**SettingValueResponseWrapperMethod**](SettingValueResponseWrapperMethod.md) |  | [optional] 
**response** | [**SettingValueResponse**](SettingValueResponse.md) |  | [optional] 
**url** | **str** | The url as specified in the corresponding request.  | [optional] 

## Example

```python
from zuora_sdk.models.setting_value_response_wrapper import SettingValueResponseWrapper

# TODO update the JSON string below
json = "{}"
# create an instance of SettingValueResponseWrapper from a JSON string
setting_value_response_wrapper_instance = SettingValueResponseWrapper.from_json(json)
# print the JSON string representation of the object
print(SettingValueResponseWrapper.to_json())

# convert the object into a dict
setting_value_response_wrapper_dict = setting_value_response_wrapper_instance.to_dict()
# create an instance of SettingValueResponseWrapper from a dict
setting_value_response_wrapper_from_dict = SettingValueResponseWrapper.from_dict(setting_value_response_wrapper_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


