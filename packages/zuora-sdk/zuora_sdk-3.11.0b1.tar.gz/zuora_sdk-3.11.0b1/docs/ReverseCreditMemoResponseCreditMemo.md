# ReverseCreditMemoResponseCreditMemo

Container for the credit memo that is automatically generated during the reversal of the invoice that is related to the credit memo. If no related invoice is reversed, the value is null.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the credit memo. | [optional] 

## Example

```python
from zuora_sdk.models.reverse_credit_memo_response_credit_memo import ReverseCreditMemoResponseCreditMemo

# TODO update the JSON string below
json = "{}"
# create an instance of ReverseCreditMemoResponseCreditMemo from a JSON string
reverse_credit_memo_response_credit_memo_instance = ReverseCreditMemoResponseCreditMemo.from_json(json)
# print the JSON string representation of the object
print(ReverseCreditMemoResponseCreditMemo.to_json())

# convert the object into a dict
reverse_credit_memo_response_credit_memo_dict = reverse_credit_memo_response_credit_memo_instance.to_dict()
# create an instance of ReverseCreditMemoResponseCreditMemo from a dict
reverse_credit_memo_response_credit_memo_from_dict = ReverseCreditMemoResponseCreditMemo.from_dict(reverse_credit_memo_response_credit_memo_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


