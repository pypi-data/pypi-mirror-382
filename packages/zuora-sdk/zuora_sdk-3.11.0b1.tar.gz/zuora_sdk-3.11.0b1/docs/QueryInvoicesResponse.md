# QueryInvoicesResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedInvoice]**](ExpandedInvoice.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_invoices_response import QueryInvoicesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryInvoicesResponse from a JSON string
query_invoices_response_instance = QueryInvoicesResponse.from_json(json)
# print the JSON string representation of the object
print(QueryInvoicesResponse.to_json())

# convert the object into a dict
query_invoices_response_dict = query_invoices_response_instance.to_dict()
# create an instance of QueryInvoicesResponse from a dict
query_invoices_response_from_dict = QueryInvoicesResponse.from_dict(query_invoices_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


