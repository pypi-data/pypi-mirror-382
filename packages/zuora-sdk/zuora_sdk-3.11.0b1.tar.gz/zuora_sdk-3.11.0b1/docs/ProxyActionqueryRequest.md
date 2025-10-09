# ProxyActionqueryRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**conf** | [**ProxyActionqueryMoreRequestConf**](ProxyActionqueryMoreRequestConf.md) |  | [optional] 
**query_string** | **str** | [ZOQL](https://knowledgecenter.zuora.com/DC_Developers/K_Zuora_Object_Query_Language) expression that specifies the object to query, the fields to retrieve, and any filters.   **Note:** When querying one time charges from ProductRatePlanCharge, you need to specify the &#x60;ChargeType&#x60; value as &#x60;One-Time&#x60; rather than &#x60;OneTime&#x60;. | 

## Example

```python
from zuora_sdk.models.proxy_actionquery_request import ProxyActionqueryRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ProxyActionqueryRequest from a JSON string
proxy_actionquery_request_instance = ProxyActionqueryRequest.from_json(json)
# print the JSON string representation of the object
print(ProxyActionqueryRequest.to_json())

# convert the object into a dict
proxy_actionquery_request_dict = proxy_actionquery_request_instance.to_dict()
# create an instance of ProxyActionqueryRequest from a dict
proxy_actionquery_request_from_dict = ProxyActionqueryRequest.from_dict(proxy_actionquery_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


