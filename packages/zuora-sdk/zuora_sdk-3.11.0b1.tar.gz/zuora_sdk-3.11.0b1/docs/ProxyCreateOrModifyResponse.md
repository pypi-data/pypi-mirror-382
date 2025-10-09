# ProxyCreateOrModifyResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**success** | **bool** |  | [optional] 

## Example

```python
from zuora_sdk.models.proxy_create_or_modify_response import ProxyCreateOrModifyResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ProxyCreateOrModifyResponse from a JSON string
proxy_create_or_modify_response_instance = ProxyCreateOrModifyResponse.from_json(json)
# print the JSON string representation of the object
print(ProxyCreateOrModifyResponse.to_json())

# convert the object into a dict
proxy_create_or_modify_response_dict = proxy_create_or_modify_response_instance.to_dict()
# create an instance of ProxyCreateOrModifyResponse from a dict
proxy_create_or_modify_response_from_dict = ProxyCreateOrModifyResponse.from_dict(proxy_create_or_modify_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


