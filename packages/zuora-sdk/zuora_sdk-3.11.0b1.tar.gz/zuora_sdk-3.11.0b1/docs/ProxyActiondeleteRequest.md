# ProxyActiondeleteRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ids** | **List[str]** | A list of one or more IDs for the objects you want to delete.  | 
**type** | **str** | The type of object that you are deleting.  | 

## Example

```python
from zuora_sdk.models.proxy_actiondelete_request import ProxyActiondeleteRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ProxyActiondeleteRequest from a JSON string
proxy_actiondelete_request_instance = ProxyActiondeleteRequest.from_json(json)
# print the JSON string representation of the object
print(ProxyActiondeleteRequest.to_json())

# convert the object into a dict
proxy_actiondelete_request_dict = proxy_actiondelete_request_instance.to_dict()
# create an instance of ProxyActiondeleteRequest from a dict
proxy_actiondelete_request_from_dict = ProxyActiondeleteRequest.from_dict(proxy_actiondelete_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


