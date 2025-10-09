# ReverseCreditMemoResponseDebitMemo

Container for the debit memo that is automatically generated during the credit memo reversal.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the debit memo. | [optional] 

## Example

```python
from zuora_sdk.models.reverse_credit_memo_response_debit_memo import ReverseCreditMemoResponseDebitMemo

# TODO update the JSON string below
json = "{}"
# create an instance of ReverseCreditMemoResponseDebitMemo from a JSON string
reverse_credit_memo_response_debit_memo_instance = ReverseCreditMemoResponseDebitMemo.from_json(json)
# print the JSON string representation of the object
print(ReverseCreditMemoResponseDebitMemo.to_json())

# convert the object into a dict
reverse_credit_memo_response_debit_memo_dict = reverse_credit_memo_response_debit_memo_instance.to_dict()
# create an instance of ReverseCreditMemoResponseDebitMemo from a dict
reverse_credit_memo_response_debit_memo_from_dict = ReverseCreditMemoResponseDebitMemo.from_dict(reverse_credit_memo_response_debit_memo_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


