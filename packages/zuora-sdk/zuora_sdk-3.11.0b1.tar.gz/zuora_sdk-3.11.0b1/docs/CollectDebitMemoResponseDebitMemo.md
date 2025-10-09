# CollectDebitMemoResponseDebitMemo

The information about the debit memo that just collected. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The unique ID of the debit memo.  | [optional] 
**number** | **str** | The unique identification number of the debit memo.  | [optional] 

## Example

```python
from zuora_sdk.models.collect_debit_memo_response_debit_memo import CollectDebitMemoResponseDebitMemo

# TODO update the JSON string below
json = "{}"
# create an instance of CollectDebitMemoResponseDebitMemo from a JSON string
collect_debit_memo_response_debit_memo_instance = CollectDebitMemoResponseDebitMemo.from_json(json)
# print the JSON string representation of the object
print(CollectDebitMemoResponseDebitMemo.to_json())

# convert the object into a dict
collect_debit_memo_response_debit_memo_dict = collect_debit_memo_response_debit_memo_instance.to_dict()
# create an instance of CollectDebitMemoResponseDebitMemo from a dict
collect_debit_memo_response_debit_memo_from_dict = CollectDebitMemoResponseDebitMemo.from_dict(collect_debit_memo_response_debit_memo_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


