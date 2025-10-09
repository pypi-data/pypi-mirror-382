# SystemHealthErrorResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**error** | **str** | Error status text.  | [optional] 
**message** | **str** | The associated reason.  | [optional] 
**path** | **str** | The system health api path having error.  | [optional] 
**status** | **int** | Error status code.  | [optional] 
**timestamp** | **datetime** | The time when error happens.  | [optional] 

## Example

```python
from zuora_sdk.models.system_health_error_response import SystemHealthErrorResponse

# TODO update the JSON string below
json = "{}"
# create an instance of SystemHealthErrorResponse from a JSON string
system_health_error_response_instance = SystemHealthErrorResponse.from_json(json)
# print the JSON string representation of the object
print(SystemHealthErrorResponse.to_json())

# convert the object into a dict
system_health_error_response_dict = system_health_error_response_instance.to_dict()
# create an instance of SystemHealthErrorResponse from a dict
system_health_error_response_from_dict = SystemHealthErrorResponse.from_dict(system_health_error_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


