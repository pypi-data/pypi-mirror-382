# SettingComponentKeyValue

Provides details about the individual components that need to be compared and deployed.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**errors** | **List[str]** |  | [optional] 
**original_payload** | **object** | Json node object contains metadata. | [optional] 
**response** | [**List[ConfigurationTemplateContent]**](ConfigurationTemplateContent.md) |  | [optional] 
**segregation_keys** | **List[str]** |  | [optional] 

## Example

```python
from zuora_sdk.models.setting_component_key_value import SettingComponentKeyValue

# TODO update the JSON string below
json = "{}"
# create an instance of SettingComponentKeyValue from a JSON string
setting_component_key_value_instance = SettingComponentKeyValue.from_json(json)
# print the JSON string representation of the object
print(SettingComponentKeyValue.to_json())

# convert the object into a dict
setting_component_key_value_dict = setting_component_key_value_instance.to_dict()
# create an instance of SettingComponentKeyValue from a dict
setting_component_key_value_from_dict = SettingComponentKeyValue.from_dict(setting_component_key_value_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


