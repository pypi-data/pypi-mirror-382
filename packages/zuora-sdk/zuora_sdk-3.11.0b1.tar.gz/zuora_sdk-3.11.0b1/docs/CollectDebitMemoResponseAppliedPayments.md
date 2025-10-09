# CollectDebitMemoResponseAppliedPayments


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**applied_amount** | **float** | The applied amount of the payment to the debit memo.  | [optional] 
**id** | **str** | The unique ID of the payment.  | [optional] 
**number** | **str** | The unique identification number of the payment.  | [optional] 
**unapplied_amount** | **float** | The unapplied amount of the payment after applied to the debit memo.  | [optional] 

## Example

```python
from zuora_sdk.models.collect_debit_memo_response_applied_payments import CollectDebitMemoResponseAppliedPayments

# TODO update the JSON string below
json = "{}"
# create an instance of CollectDebitMemoResponseAppliedPayments from a JSON string
collect_debit_memo_response_applied_payments_instance = CollectDebitMemoResponseAppliedPayments.from_json(json)
# print the JSON string representation of the object
print(CollectDebitMemoResponseAppliedPayments.to_json())

# convert the object into a dict
collect_debit_memo_response_applied_payments_dict = collect_debit_memo_response_applied_payments_instance.to_dict()
# create an instance of CollectDebitMemoResponseAppliedPayments from a dict
collect_debit_memo_response_applied_payments_from_dict = CollectDebitMemoResponseAppliedPayments.from_dict(collect_debit_memo_response_applied_payments_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


