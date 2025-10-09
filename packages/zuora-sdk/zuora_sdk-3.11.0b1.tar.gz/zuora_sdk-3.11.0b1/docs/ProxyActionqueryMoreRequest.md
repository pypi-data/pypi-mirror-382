# ProxyActionqueryMoreRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**conf** | [**ProxyActionqueryMoreRequestConf**](ProxyActionqueryMoreRequestConf.md) |  | [optional] 
**query_locator** | **str** | A marker passed to QueryMore to get the next set of results. | 

## Example

```python
from zuora_sdk.models.proxy_actionquery_more_request import ProxyActionqueryMoreRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ProxyActionqueryMoreRequest from a JSON string
proxy_actionquery_more_request_instance = ProxyActionqueryMoreRequest.from_json(json)
# print the JSON string representation of the object
print(ProxyActionqueryMoreRequest.to_json())

# convert the object into a dict
proxy_actionquery_more_request_dict = proxy_actionquery_more_request_instance.to_dict()
# create an instance of ProxyActionqueryMoreRequest from a dict
proxy_actionquery_more_request_from_dict = ProxyActionqueryMoreRequest.from_dict(proxy_actionquery_more_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


