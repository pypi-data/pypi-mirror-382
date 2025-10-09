# BadRequestErrors


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | **str** | The error code. | [optional] 
**status** | **str** | The status of the response. | [optional] 
**title** | **str** | The reason for the error. | [optional] 

## Example

```python
from zuora_sdk.models.bad_request_errors import BadRequestErrors

# TODO update the JSON string below
json = "{}"
# create an instance of BadRequestErrors from a JSON string
bad_request_errors_instance = BadRequestErrors.from_json(json)
# print the JSON string representation of the object
print(BadRequestErrors.to_json())

# convert the object into a dict
bad_request_errors_dict = bad_request_errors_instance.to_dict()
# create an instance of BadRequestErrors from a dict
bad_request_errors_from_dict = BadRequestErrors.from_dict(bad_request_errors_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


