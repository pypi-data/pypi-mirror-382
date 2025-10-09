# SettingItemHttpOperation


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**method** | [**SettingItemHttpOperationMethod**](SettingItemHttpOperationMethod.md) |  | [optional] 
**parameters** | [**List[SettingItemHttpRequestParameter]**](SettingItemHttpRequestParameter.md) | An array of paramters required by this operation. | [optional] 
**request_type** | **object** | JSON Schema for the request body of this operation. | [optional] 
**response_type** | **object** | JSON Schema for the response body of this operation. | [optional] 
**url** | **str** | The endpoint url of the operation method. For example, &#x60;/settings/billing-rules&#x60;. | [optional] 

## Example

```python
from zuora_sdk.models.setting_item_http_operation import SettingItemHttpOperation

# TODO update the JSON string below
json = "{}"
# create an instance of SettingItemHttpOperation from a JSON string
setting_item_http_operation_instance = SettingItemHttpOperation.from_json(json)
# print the JSON string representation of the object
print(SettingItemHttpOperation.to_json())

# convert the object into a dict
setting_item_http_operation_dict = setting_item_http_operation_instance.to_dict()
# create an instance of SettingItemHttpOperation from a dict
setting_item_http_operation_from_dict = SettingItemHttpOperation.from_dict(setting_item_http_operation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


