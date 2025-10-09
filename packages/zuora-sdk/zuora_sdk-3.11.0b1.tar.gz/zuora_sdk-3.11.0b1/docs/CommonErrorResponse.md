# CommonErrorResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | **int** | The error code.  | [optional] 
**message** | **str** | The error message.  | [optional] 

## Example

```python
from zuora_sdk.models.common_error_response import CommonErrorResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CommonErrorResponse from a JSON string
common_error_response_instance = CommonErrorResponse.from_json(json)
# print the JSON string representation of the object
print(CommonErrorResponse.to_json())

# convert the object into a dict
common_error_response_dict = common_error_response_instance.to_dict()
# create an instance of CommonErrorResponse from a dict
common_error_response_from_dict = CommonErrorResponse.from_dict(common_error_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


