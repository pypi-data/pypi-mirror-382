# ProxyBadRequestResponseErrorsInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | **str** |  | [optional] 
**message** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.proxy_bad_request_response_errors_inner import ProxyBadRequestResponseErrorsInner

# TODO update the JSON string below
json = "{}"
# create an instance of ProxyBadRequestResponseErrorsInner from a JSON string
proxy_bad_request_response_errors_inner_instance = ProxyBadRequestResponseErrorsInner.from_json(json)
# print the JSON string representation of the object
print(ProxyBadRequestResponseErrorsInner.to_json())

# convert the object into a dict
proxy_bad_request_response_errors_inner_dict = proxy_bad_request_response_errors_inner_instance.to_dict()
# create an instance of ProxyBadRequestResponseErrorsInner from a dict
proxy_bad_request_response_errors_inner_from_dict = ProxyBadRequestResponseErrorsInner.from_dict(proxy_bad_request_response_errors_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


