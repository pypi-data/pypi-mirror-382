# QueryDebitMemoItemsResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedDebitMemoItem]**](ExpandedDebitMemoItem.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_debit_memo_items_response import QueryDebitMemoItemsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryDebitMemoItemsResponse from a JSON string
query_debit_memo_items_response_instance = QueryDebitMemoItemsResponse.from_json(json)
# print the JSON string representation of the object
print(QueryDebitMemoItemsResponse.to_json())

# convert the object into a dict
query_debit_memo_items_response_dict = query_debit_memo_items_response_instance.to_dict()
# create an instance of QueryDebitMemoItemsResponse from a dict
query_debit_memo_items_response_from_dict = QueryDebitMemoItemsResponse.from_dict(query_debit_memo_items_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


