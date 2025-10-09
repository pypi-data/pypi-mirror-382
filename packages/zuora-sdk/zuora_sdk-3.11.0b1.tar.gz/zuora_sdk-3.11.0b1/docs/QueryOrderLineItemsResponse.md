# QueryOrderLineItemsResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedOrderLineItem]**](ExpandedOrderLineItem.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_order_line_items_response import QueryOrderLineItemsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryOrderLineItemsResponse from a JSON string
query_order_line_items_response_instance = QueryOrderLineItemsResponse.from_json(json)
# print the JSON string representation of the object
print(QueryOrderLineItemsResponse.to_json())

# convert the object into a dict
query_order_line_items_response_dict = query_order_line_items_response_instance.to_dict()
# create an instance of QueryOrderLineItemsResponse from a dict
query_order_line_items_response_from_dict = QueryOrderLineItemsResponse.from_dict(query_order_line_items_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


