# SignUpResponseReasons


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | **str** | The error code of response.  | [optional] 
**message** | **str** | The detail information of the error response  | [optional] 

## Example

```python
from zuora_sdk.models.sign_up_response_reasons import SignUpResponseReasons

# TODO update the JSON string below
json = "{}"
# create an instance of SignUpResponseReasons from a JSON string
sign_up_response_reasons_instance = SignUpResponseReasons.from_json(json)
# print the JSON string representation of the object
print(SignUpResponseReasons.to_json())

# convert the object into a dict
sign_up_response_reasons_dict = sign_up_response_reasons_instance.to_dict()
# create an instance of SignUpResponseReasons from a dict
sign_up_response_reasons_from_dict = SignUpResponseReasons.from_dict(sign_up_response_reasons_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


