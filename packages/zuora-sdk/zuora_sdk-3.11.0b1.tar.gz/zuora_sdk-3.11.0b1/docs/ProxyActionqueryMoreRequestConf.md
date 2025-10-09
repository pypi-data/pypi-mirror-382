# ProxyActionqueryMoreRequestConf

Configuration of the query result.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**batch_size** | **int** | Defines the batch size of the query result. The range is 1 - 2000 (inclusive). If a value higher than 2000 is submitted, only 2000 results are returned. | [optional] 

## Example

```python
from zuora_sdk.models.proxy_actionquery_more_request_conf import ProxyActionqueryMoreRequestConf

# TODO update the JSON string below
json = "{}"
# create an instance of ProxyActionqueryMoreRequestConf from a JSON string
proxy_actionquery_more_request_conf_instance = ProxyActionqueryMoreRequestConf.from_json(json)
# print the JSON string representation of the object
print(ProxyActionqueryMoreRequestConf.to_json())

# convert the object into a dict
proxy_actionquery_more_request_conf_dict = proxy_actionquery_more_request_conf_instance.to_dict()
# create an instance of ProxyActionqueryMoreRequestConf from a dict
proxy_actionquery_more_request_conf_from_dict = ProxyActionqueryMoreRequestConf.from_dict(proxy_actionquery_more_request_conf_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


