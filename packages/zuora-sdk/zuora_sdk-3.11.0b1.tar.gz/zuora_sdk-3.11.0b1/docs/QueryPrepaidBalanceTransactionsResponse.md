# QueryPrepaidBalanceTransactionsResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedPrepaidBalanceTransaction]**](ExpandedPrepaidBalanceTransaction.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_prepaid_balance_transactions_response import QueryPrepaidBalanceTransactionsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryPrepaidBalanceTransactionsResponse from a JSON string
query_prepaid_balance_transactions_response_instance = QueryPrepaidBalanceTransactionsResponse.from_json(json)
# print the JSON string representation of the object
print(QueryPrepaidBalanceTransactionsResponse.to_json())

# convert the object into a dict
query_prepaid_balance_transactions_response_dict = query_prepaid_balance_transactions_response_instance.to_dict()
# create an instance of QueryPrepaidBalanceTransactionsResponse from a dict
query_prepaid_balance_transactions_response_from_dict = QueryPrepaidBalanceTransactionsResponse.from_dict(query_prepaid_balance_transactions_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


