# CollectDebitMemoResponseAppliedCreditMemos


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**applied_amount** | **float** | The applied amount of the credit memo to the debit memo.  | [optional] 
**id** | **str** | The unique ID of the credit memo.  | [optional] 
**number** | **str** | The unique identification number of the credit memo.  | [optional] 
**unapplied_amount** | **float** | The unapplied amount of the credit memo after applied to the debit memo. | [optional] 

## Example

```python
from zuora_sdk.models.collect_debit_memo_response_applied_credit_memos import CollectDebitMemoResponseAppliedCreditMemos

# TODO update the JSON string below
json = "{}"
# create an instance of CollectDebitMemoResponseAppliedCreditMemos from a JSON string
collect_debit_memo_response_applied_credit_memos_instance = CollectDebitMemoResponseAppliedCreditMemos.from_json(json)
# print the JSON string representation of the object
print(CollectDebitMemoResponseAppliedCreditMemos.to_json())

# convert the object into a dict
collect_debit_memo_response_applied_credit_memos_dict = collect_debit_memo_response_applied_credit_memos_instance.to_dict()
# create an instance of CollectDebitMemoResponseAppliedCreditMemos from a dict
collect_debit_memo_response_applied_credit_memos_from_dict = CollectDebitMemoResponseAppliedCreditMemos.from_dict(collect_debit_memo_response_applied_credit_memos_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


