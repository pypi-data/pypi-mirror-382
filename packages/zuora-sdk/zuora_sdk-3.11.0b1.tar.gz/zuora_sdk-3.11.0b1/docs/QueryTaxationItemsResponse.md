# QueryTaxationItemsResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedTaxationItem]**](ExpandedTaxationItem.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_taxation_items_response import QueryTaxationItemsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryTaxationItemsResponse from a JSON string
query_taxation_items_response_instance = QueryTaxationItemsResponse.from_json(json)
# print the JSON string representation of the object
print(QueryTaxationItemsResponse.to_json())

# convert the object into a dict
query_taxation_items_response_dict = query_taxation_items_response_instance.to_dict()
# create an instance of QueryTaxationItemsResponse from a dict
query_taxation_items_response_from_dict = QueryTaxationItemsResponse.from_dict(query_taxation_items_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


