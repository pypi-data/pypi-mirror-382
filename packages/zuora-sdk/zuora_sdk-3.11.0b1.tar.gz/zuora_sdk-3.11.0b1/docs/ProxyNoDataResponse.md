# ProxyNoDataResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**done** | **bool** |  | [optional] 
**records** | **List[object]** |  | [optional] 
**size** | **int** |  | [optional] 

## Example

```python
from zuora_sdk.models.proxy_no_data_response import ProxyNoDataResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ProxyNoDataResponse from a JSON string
proxy_no_data_response_instance = ProxyNoDataResponse.from_json(json)
# print the JSON string representation of the object
print(ProxyNoDataResponse.to_json())

# convert the object into a dict
proxy_no_data_response_dict = proxy_no_data_response_instance.to_dict()
# create an instance of ProxyNoDataResponse from a dict
proxy_no_data_response_from_dict = ProxyNoDataResponse.from_dict(proxy_no_data_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


