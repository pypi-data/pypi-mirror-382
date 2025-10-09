# QueryInvoiceItemsResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedInvoiceItem]**](ExpandedInvoiceItem.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_invoice_items_response import QueryInvoiceItemsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryInvoiceItemsResponse from a JSON string
query_invoice_items_response_instance = QueryInvoiceItemsResponse.from_json(json)
# print the JSON string representation of the object
print(QueryInvoiceItemsResponse.to_json())

# convert the object into a dict
query_invoice_items_response_dict = query_invoice_items_response_instance.to_dict()
# create an instance of QueryInvoiceItemsResponse from a dict
query_invoice_items_response_from_dict = QueryInvoiceItemsResponse.from_dict(query_invoice_items_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


