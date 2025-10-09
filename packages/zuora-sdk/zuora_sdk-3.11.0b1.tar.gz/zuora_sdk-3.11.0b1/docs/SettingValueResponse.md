# SettingValueResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**body** | **Dict[str, object]** | Response body if the request is executed successfully. | [optional] 
**error_messages** | **List[str]** | An array of error messages if errors occur when executing the request.  | [optional] 
**status** | **str** | User readable response status, for example, 502 BAD_GATEWAY.  | [optional] 

## Example

```python
from zuora_sdk.models.setting_value_response import SettingValueResponse

# TODO update the JSON string below
json = "{}"
# create an instance of SettingValueResponse from a JSON string
setting_value_response_instance = SettingValueResponse.from_json(json)
# print the JSON string representation of the object
print(SettingValueResponse.to_json())

# convert the object into a dict
setting_value_response_dict = setting_value_response_instance.to_dict()
# create an instance of SettingValueResponse from a dict
setting_value_response_from_dict = SettingValueResponse.from_dict(setting_value_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


