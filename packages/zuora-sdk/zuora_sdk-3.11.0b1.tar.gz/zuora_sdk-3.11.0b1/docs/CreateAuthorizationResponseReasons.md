# CreateAuthorizationResponseReasons


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | **str** | Error code.  | [optional] 
**message** | **str** | Error message. It usually contains a combination of gateway response code and response message. | [optional] 

## Example

```python
from zuora_sdk.models.create_authorization_response_reasons import CreateAuthorizationResponseReasons

# TODO update the JSON string below
json = "{}"
# create an instance of CreateAuthorizationResponseReasons from a JSON string
create_authorization_response_reasons_instance = CreateAuthorizationResponseReasons.from_json(json)
# print the JSON string representation of the object
print(CreateAuthorizationResponseReasons.to_json())

# convert the object into a dict
create_authorization_response_reasons_dict = create_authorization_response_reasons_instance.to_dict()
# create an instance of CreateAuthorizationResponseReasons from a dict
create_authorization_response_reasons_from_dict = CreateAuthorizationResponseReasons.from_dict(create_authorization_response_reasons_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


