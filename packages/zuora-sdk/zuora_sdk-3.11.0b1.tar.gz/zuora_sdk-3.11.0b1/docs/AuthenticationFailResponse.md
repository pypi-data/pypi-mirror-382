# AuthenticationFailResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** |  | [optional] 
**message** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.authentication_fail_response import AuthenticationFailResponse

# TODO update the JSON string below
json = "{}"
# create an instance of AuthenticationFailResponse from a JSON string
authentication_fail_response_instance = AuthenticationFailResponse.from_json(json)
# print the JSON string representation of the object
print(AuthenticationFailResponse.to_json())

# convert the object into a dict
authentication_fail_response_dict = authentication_fail_response_instance.to_dict()
# create an instance of AuthenticationFailResponse from a dict
authentication_fail_response_from_dict = AuthenticationFailResponse.from_dict(authentication_fail_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


