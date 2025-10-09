# SettingSourceComponent

Provides details about the different components that need to be compared and deployed.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_fields** | [**List[SettingComponentKeyValue]**](SettingComponentKeyValue.md) |  | [optional] 
**custom_objects** | [**List[SettingComponentKeyValue]**](SettingComponentKeyValue.md) |  | [optional] 
**data_access_control** | [**List[SettingComponentKeyValue]**](SettingComponentKeyValue.md) |  | [optional] 
**notifications** | [**List[SettingComponentKeyValue]**](SettingComponentKeyValue.md) |  | [optional] 
**product_catalog** | [**List[SettingComponentKeyValue]**](SettingComponentKeyValue.md) |  | [optional] 
**settings** | [**List[SettingComponentKeyValue]**](SettingComponentKeyValue.md) |  | [optional] 
**workflows** | [**List[SettingComponentKeyValue]**](SettingComponentKeyValue.md) |  | [optional] 
**user_roles** | [**List[SettingComponentKeyValue]**](SettingComponentKeyValue.md) |  | [optional] 
**taxation** | [**List[SettingComponentKeyValue]**](SettingComponentKeyValue.md) |  | [optional] 
**billing_documents** | [**List[SettingComponentKeyValue]**](SettingComponentKeyValue.md) |  | [optional] 
**reporting** | [**List[SettingComponentKeyValue]**](SettingComponentKeyValue.md) |  | [optional] 
**revenue** | [**List[SettingComponentKeyValue]**](SettingComponentKeyValue.md) |  | [optional] 
**mediation** | [**List[SettingComponentKeyValue]**](SettingComponentKeyValue.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.setting_source_component import SettingSourceComponent

# TODO update the JSON string below
json = "{}"
# create an instance of SettingSourceComponent from a JSON string
setting_source_component_instance = SettingSourceComponent.from_json(json)
# print the JSON string representation of the object
print(SettingSourceComponent.to_json())

# convert the object into a dict
setting_source_component_dict = setting_source_component_instance.to_dict()
# create an instance of SettingSourceComponent from a dict
setting_source_component_from_dict = SettingSourceComponent.from_dict(setting_source_component_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


