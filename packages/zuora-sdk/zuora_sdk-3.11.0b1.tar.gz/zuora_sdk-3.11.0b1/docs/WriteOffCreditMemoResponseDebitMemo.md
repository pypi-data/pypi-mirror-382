# WriteOffCreditMemoResponseDebitMemo

Container for the credit memo that is automatically created. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The unique ID of the created debit memo.  | [optional] 

## Example

```python
from zuora_sdk.models.write_off_credit_memo_response_debit_memo import WriteOffCreditMemoResponseDebitMemo

# TODO update the JSON string below
json = "{}"
# create an instance of WriteOffCreditMemoResponseDebitMemo from a JSON string
write_off_credit_memo_response_debit_memo_instance = WriteOffCreditMemoResponseDebitMemo.from_json(json)
# print the JSON string representation of the object
print(WriteOffCreditMemoResponseDebitMemo.to_json())

# convert the object into a dict
write_off_credit_memo_response_debit_memo_dict = write_off_credit_memo_response_debit_memo_instance.to_dict()
# create an instance of WriteOffCreditMemoResponseDebitMemo from a dict
write_off_credit_memo_response_debit_memo_from_dict = WriteOffCreditMemoResponseDebitMemo.from_dict(write_off_credit_memo_response_debit_memo_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


