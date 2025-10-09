# ProxyUnauthorizedResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** | Error message.   If the error message is \&quot;Authentication error\&quot;, ensure that the &#x60;Authorization&#x60; request header contains valid authentication credentials, then retry the request. See [Authentication](https://www.zuora.com/developer/rest-api/general-concepts/authentication/) for more information.   If the error message is \&quot;Failed to get user info\&quot;, retry the request. | [optional] 

## Example

```python
from zuora_sdk.models.proxy_unauthorized_response import ProxyUnauthorizedResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ProxyUnauthorizedResponse from a JSON string
proxy_unauthorized_response_instance = ProxyUnauthorizedResponse.from_json(json)
# print the JSON string representation of the object
print(ProxyUnauthorizedResponse.to_json())

# convert the object into a dict
proxy_unauthorized_response_dict = proxy_unauthorized_response_instance.to_dict()
# create an instance of ProxyUnauthorizedResponse from a dict
proxy_unauthorized_response_from_dict = ProxyUnauthorizedResponse.from_dict(proxy_unauthorized_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


