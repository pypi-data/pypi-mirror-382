# QueryCreditMemosResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedCreditMemo]**](ExpandedCreditMemo.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_credit_memos_response import QueryCreditMemosResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryCreditMemosResponse from a JSON string
query_credit_memos_response_instance = QueryCreditMemosResponse.from_json(json)
# print the JSON string representation of the object
print(QueryCreditMemosResponse.to_json())

# convert the object into a dict
query_credit_memos_response_dict = query_credit_memos_response_instance.to_dict()
# create an instance of QueryCreditMemosResponse from a dict
query_credit_memos_response_from_dict = QueryCreditMemosResponse.from_dict(query_credit_memos_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


