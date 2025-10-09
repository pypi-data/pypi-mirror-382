# ProxyActioncreateRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**objects** | **List[Dict[str, object]]** |  | 
**type** | **str** |  | 

## Example

```python
from zuora_sdk.models.proxy_actioncreate_request import ProxyActioncreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ProxyActioncreateRequest from a JSON string
proxy_actioncreate_request_instance = ProxyActioncreateRequest.from_json(json)
# print the JSON string representation of the object
print(ProxyActioncreateRequest.to_json())

# convert the object into a dict
proxy_actioncreate_request_dict = proxy_actioncreate_request_instance.to_dict()
# create an instance of ProxyActioncreateRequest from a dict
proxy_actioncreate_request_from_dict = ProxyActioncreateRequest.from_dict(proxy_actioncreate_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


