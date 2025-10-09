# ErrorResponseReasonsInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | **str** | The error code of response.  | [optional] 
**message** | **str** | The detail information of the error response | [optional] 

## Example

```python
from zuora_sdk.models.error_response_reasons_inner import ErrorResponseReasonsInner

# TODO update the JSON string below
json = "{}"
# create an instance of ErrorResponseReasonsInner from a JSON string
error_response_reasons_inner_instance = ErrorResponseReasonsInner.from_json(json)
# print the JSON string representation of the object
print(ErrorResponseReasonsInner.to_json())

# convert the object into a dict
error_response_reasons_inner_dict = error_response_reasons_inner_instance.to_dict()
# create an instance of ErrorResponseReasonsInner from a dict
error_response_reasons_inner_from_dict = ErrorResponseReasonsInner.from_dict(error_response_reasons_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


