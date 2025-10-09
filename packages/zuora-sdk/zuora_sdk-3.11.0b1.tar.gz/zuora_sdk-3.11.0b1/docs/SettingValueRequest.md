# SettingValueRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**body** | **Dict[str, object]** | Request payload if any | [optional] 
**children** | [**List[ChildrenSettingValueRequest]**](ChildrenSettingValueRequest.md) | An array of requests that can only be executed after its parent request has been executed successfully.  | [optional] 
**id** | **str** | The id of the request. You can set it to any string. It must be unique within the whole batch.  | [optional] 
**method** | [**SettingValueRequestMethod**](SettingValueRequestMethod.md) |  | [optional] 
**url** | **str** | The relative URL of the setting. It is the same as in the &#x60;pathPattern&#x60; field in the response body of [Listing all Settings](https://www.zuora.com/developer/api-references/api/operation/Get_ListAllSettings). For example, &#x60;/billing-rules&#x60;.  | [optional] 

## Example

```python
from zuora_sdk.models.setting_value_request import SettingValueRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SettingValueRequest from a JSON string
setting_value_request_instance = SettingValueRequest.from_json(json)
# print the JSON string representation of the object
print(SettingValueRequest.to_json())

# convert the object into a dict
setting_value_request_dict = setting_value_request_instance.to_dict()
# create an instance of SettingValueRequest from a dict
setting_value_request_from_dict = SettingValueRequest.from_dict(setting_value_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


