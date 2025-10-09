# ProxyDeleteResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**success** | **bool** |  | [optional] 

## Example

```python
from zuora_sdk.models.proxy_delete_response import ProxyDeleteResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ProxyDeleteResponse from a JSON string
proxy_delete_response_instance = ProxyDeleteResponse.from_json(json)
# print the JSON string representation of the object
print(ProxyDeleteResponse.to_json())

# convert the object into a dict
proxy_delete_response_dict = proxy_delete_response_instance.to_dict()
# create an instance of ProxyDeleteResponse from a dict
proxy_delete_response_from_dict = ProxyDeleteResponse.from_dict(proxy_delete_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


