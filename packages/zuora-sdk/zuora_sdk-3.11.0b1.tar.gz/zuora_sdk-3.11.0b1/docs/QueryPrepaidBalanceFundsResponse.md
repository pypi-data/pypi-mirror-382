# QueryPrepaidBalanceFundsResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedPrepaidBalanceFund]**](ExpandedPrepaidBalanceFund.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_prepaid_balance_funds_response import QueryPrepaidBalanceFundsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryPrepaidBalanceFundsResponse from a JSON string
query_prepaid_balance_funds_response_instance = QueryPrepaidBalanceFundsResponse.from_json(json)
# print the JSON string representation of the object
print(QueryPrepaidBalanceFundsResponse.to_json())

# convert the object into a dict
query_prepaid_balance_funds_response_dict = query_prepaid_balance_funds_response_instance.to_dict()
# create an instance of QueryPrepaidBalanceFundsResponse from a dict
query_prepaid_balance_funds_response_from_dict = QueryPrepaidBalanceFundsResponse.from_dict(query_prepaid_balance_funds_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


