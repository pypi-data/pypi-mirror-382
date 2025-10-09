# QueryPrepaidBalancesResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedPrepaidBalance]**](ExpandedPrepaidBalance.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_prepaid_balances_response import QueryPrepaidBalancesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryPrepaidBalancesResponse from a JSON string
query_prepaid_balances_response_instance = QueryPrepaidBalancesResponse.from_json(json)
# print the JSON string representation of the object
print(QueryPrepaidBalancesResponse.to_json())

# convert the object into a dict
query_prepaid_balances_response_dict = query_prepaid_balances_response_instance.to_dict()
# create an instance of QueryPrepaidBalancesResponse from a dict
query_prepaid_balances_response_from_dict = QueryPrepaidBalancesResponse.from_dict(query_prepaid_balances_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


