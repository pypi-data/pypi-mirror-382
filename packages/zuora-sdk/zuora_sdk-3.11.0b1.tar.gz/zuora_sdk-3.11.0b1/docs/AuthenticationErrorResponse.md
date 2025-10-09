# AuthenticationErrorResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** |  | [optional] 
**message** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.authentication_error_response import AuthenticationErrorResponse

# TODO update the JSON string below
json = "{}"
# create an instance of AuthenticationErrorResponse from a JSON string
authentication_error_response_instance = AuthenticationErrorResponse.from_json(json)
# print the JSON string representation of the object
print(AuthenticationErrorResponse.to_json())

# convert the object into a dict
authentication_error_response_dict = authentication_error_response_instance.to_dict()
# create an instance of AuthenticationErrorResponse from a dict
authentication_error_response_from_dict = AuthenticationErrorResponse.from_dict(authentication_error_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


