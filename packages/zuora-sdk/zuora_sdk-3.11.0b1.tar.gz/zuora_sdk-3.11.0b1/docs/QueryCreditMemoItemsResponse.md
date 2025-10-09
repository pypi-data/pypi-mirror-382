# QueryCreditMemoItemsResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedCreditMemoItem]**](ExpandedCreditMemoItem.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_credit_memo_items_response import QueryCreditMemoItemsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryCreditMemoItemsResponse from a JSON string
query_credit_memo_items_response_instance = QueryCreditMemoItemsResponse.from_json(json)
# print the JSON string representation of the object
print(QueryCreditMemoItemsResponse.to_json())

# convert the object into a dict
query_credit_memo_items_response_dict = query_credit_memo_items_response_instance.to_dict()
# create an instance of QueryCreditMemoItemsResponse from a dict
query_credit_memo_items_response_from_dict = QueryCreditMemoItemsResponse.from_dict(query_credit_memo_items_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


