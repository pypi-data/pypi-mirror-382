# QueryOrderssResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedOrders]**](ExpandedOrders.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_orderss_response import QueryOrderssResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryOrderssResponse from a JSON string
query_orderss_response_instance = QueryOrderssResponse.from_json(json)
# print the JSON string representation of the object
print(QueryOrderssResponse.to_json())

# convert the object into a dict
query_orderss_response_dict = query_orderss_response_instance.to_dict()
# create an instance of QueryOrderssResponse from a dict
query_orderss_response_from_dict = QueryOrderssResponse.from_dict(query_orderss_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


