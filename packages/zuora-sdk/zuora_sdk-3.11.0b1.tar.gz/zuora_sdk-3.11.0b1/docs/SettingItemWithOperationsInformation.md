# SettingItemWithOperationsInformation


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**context** | [**SettingItemWithOperationsInformationContext**](SettingItemWithOperationsInformationContext.md) |  | [optional] 
**description** | **str** | The description of the setting item as you see from Zuora UI. | [optional] 
**http_operations** | [**List[SettingItemHttpOperation]**](SettingItemHttpOperation.md) | An array of HTTP operation methods that are supported on this setting endpoint. | [optional] 
**key** | **str** | The unique key to distinguish the setting item. | [optional] 
**path_pattern** | **str** | The path pattern of the setting endpoint, relative to &#x60;/settings&#x60;. For example, &#x60;/billing-rules&#x60;. | [optional] 

## Example

```python
from zuora_sdk.models.setting_item_with_operations_information import SettingItemWithOperationsInformation

# TODO update the JSON string below
json = "{}"
# create an instance of SettingItemWithOperationsInformation from a JSON string
setting_item_with_operations_information_instance = SettingItemWithOperationsInformation.from_json(json)
# print the JSON string representation of the object
print(SettingItemWithOperationsInformation.to_json())

# convert the object into a dict
setting_item_with_operations_information_dict = setting_item_with_operations_information_instance.to_dict()
# create an instance of SettingItemWithOperationsInformation from a dict
setting_item_with_operations_information_from_dict = SettingItemWithOperationsInformation.from_dict(setting_item_with_operations_information_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


