# ProxyBadRequestResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**errors** | [**List[ProxyBadRequestResponseErrorsInner]**](ProxyBadRequestResponseErrorsInner.md) |  | [optional] 
**success** | **bool** |  | [optional] 

## Example

```python
from zuora_sdk.models.proxy_bad_request_response import ProxyBadRequestResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ProxyBadRequestResponse from a JSON string
proxy_bad_request_response_instance = ProxyBadRequestResponse.from_json(json)
# print the JSON string representation of the object
print(ProxyBadRequestResponse.to_json())

# convert the object into a dict
proxy_bad_request_response_dict = proxy_bad_request_response_instance.to_dict()
# create an instance of ProxyBadRequestResponse from a dict
proxy_bad_request_response_from_dict = ProxyBadRequestResponse.from_dict(proxy_bad_request_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


