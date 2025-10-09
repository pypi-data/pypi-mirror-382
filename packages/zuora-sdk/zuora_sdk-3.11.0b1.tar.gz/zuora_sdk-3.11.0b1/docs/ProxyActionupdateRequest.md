# ProxyActionupdateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**objects** | [**List[ZObjectUpdate]**](ZObjectUpdate.md) |  | 
**type** | **str** |  | 

## Example

```python
from zuora_sdk.models.proxy_actionupdate_request import ProxyActionupdateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ProxyActionupdateRequest from a JSON string
proxy_actionupdate_request_instance = ProxyActionupdateRequest.from_json(json)
# print the JSON string representation of the object
print(ProxyActionupdateRequest.to_json())

# convert the object into a dict
proxy_actionupdate_request_dict = proxy_actionupdate_request_instance.to_dict()
# create an instance of ProxyActionupdateRequest from a dict
proxy_actionupdate_request_from_dict = ProxyActionupdateRequest.from_dict(proxy_actionupdate_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


