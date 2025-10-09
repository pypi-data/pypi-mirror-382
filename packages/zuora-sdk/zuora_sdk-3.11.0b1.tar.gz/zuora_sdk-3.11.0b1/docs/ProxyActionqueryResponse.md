# ProxyActionqueryResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**done** | **bool** | Indicates whether the returned records contain all the query results. * If the &#x60;queryLocator&#x60; field is returned, this field is set to &#x60;false&#x60;. * If no &#x60;queryLocator&#x60; field is returned, this field is set to &#x60;true&#x60;.  | [optional] 
**query_locator** | **str** | A marker passed to QueryMore to get the next set of results. For more information, see [QueryMore](https://www.zuora.com/developer/api-references/api/operation/Action_PostqueryMore/). | [optional] 
**records** | **List[Dict[str, object]]** | A list of queried results. | [optional] 
**size** | **int** | The number of the returned query results. | [optional] 

## Example

```python
from zuora_sdk.models.proxy_actionquery_response import ProxyActionqueryResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ProxyActionqueryResponse from a JSON string
proxy_actionquery_response_instance = ProxyActionqueryResponse.from_json(json)
# print the JSON string representation of the object
print(ProxyActionqueryResponse.to_json())

# convert the object into a dict
proxy_actionquery_response_dict = proxy_actionquery_response_instance.to_dict()
# create an instance of ProxyActionqueryResponse from a dict
proxy_actionquery_response_from_dict = ProxyActionqueryResponse.from_dict(proxy_actionquery_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


