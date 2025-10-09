# SettingItemHttpRequestParameter


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** | The description of the paramter. | [optional] 
**name** | **str** | The name of the parameter. | [optional] 

## Example

```python
from zuora_sdk.models.setting_item_http_request_parameter import SettingItemHttpRequestParameter

# TODO update the JSON string below
json = "{}"
# create an instance of SettingItemHttpRequestParameter from a JSON string
setting_item_http_request_parameter_instance = SettingItemHttpRequestParameter.from_json(json)
# print the JSON string representation of the object
print(SettingItemHttpRequestParameter.to_json())

# convert the object into a dict
setting_item_http_request_parameter_dict = setting_item_http_request_parameter_instance.to_dict()
# create an instance of SettingItemHttpRequestParameter from a dict
setting_item_http_request_parameter_from_dict = SettingItemHttpRequestParameter.from_dict(setting_item_http_request_parameter_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


