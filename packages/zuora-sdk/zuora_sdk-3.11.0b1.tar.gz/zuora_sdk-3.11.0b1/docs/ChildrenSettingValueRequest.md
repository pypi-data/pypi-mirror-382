# ChildrenSettingValueRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**body** | **Dict[str, object]** | Request payload if any | [optional] 
**id** | **str** | The id of the request. You can set it to any string. It must be unique within the whole batch.  | [optional] 
**method** | [**ChildrenSettingValueRequestMethod**](ChildrenSettingValueRequestMethod.md) |  | [optional] 
**url** | **str** | The relative URL of the setting. It is the same as in the &#x60;pathPattern&#x60; field in the response body of [Listing all settings](https://www.zuora.com/developer/api-references/api/operation/Get_ListAllSettings). For example, &#x60;/billing-rules&#x60;.  | [optional] 

## Example

```python
from zuora_sdk.models.children_setting_value_request import ChildrenSettingValueRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ChildrenSettingValueRequest from a JSON string
children_setting_value_request_instance = ChildrenSettingValueRequest.from_json(json)
# print the JSON string representation of the object
print(ChildrenSettingValueRequest.to_json())

# convert the object into a dict
children_setting_value_request_dict = children_setting_value_request_instance.to_dict()
# create an instance of ChildrenSettingValueRequest from a dict
children_setting_value_request_from_dict = ChildrenSettingValueRequest.from_dict(children_setting_value_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


