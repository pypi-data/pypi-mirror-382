# QueryDebitMemosResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedDebitMemo]**](ExpandedDebitMemo.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_debit_memos_response import QueryDebitMemosResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryDebitMemosResponse from a JSON string
query_debit_memos_response_instance = QueryDebitMemosResponse.from_json(json)
# print the JSON string representation of the object
print(QueryDebitMemosResponse.to_json())

# convert the object into a dict
query_debit_memos_response_dict = query_debit_memos_response_instance.to_dict()
# create an instance of QueryDebitMemosResponse from a dict
query_debit_memos_response_from_dict = QueryDebitMemosResponse.from_dict(query_debit_memos_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


