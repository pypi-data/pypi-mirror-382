# QueryRefundApplicationItemsResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedRefundApplicationItem]**](ExpandedRefundApplicationItem.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_refund_application_items_response import QueryRefundApplicationItemsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryRefundApplicationItemsResponse from a JSON string
query_refund_application_items_response_instance = QueryRefundApplicationItemsResponse.from_json(json)
# print the JSON string representation of the object
print(QueryRefundApplicationItemsResponse.to_json())

# convert the object into a dict
query_refund_application_items_response_dict = query_refund_application_items_response_instance.to_dict()
# create an instance of QueryRefundApplicationItemsResponse from a dict
query_refund_application_items_response_from_dict = QueryRefundApplicationItemsResponse.from_dict(query_refund_application_items_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


