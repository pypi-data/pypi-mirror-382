# ReverseInvoiceResponseDebitMemo

Container for the debit memo that is automatically generated during the reversal of the credit memo related to this invoice. If no related credit memo is reversed, this field is not retruned in the response body.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the debit memo. | [optional] 

## Example

```python
from zuora_sdk.models.reverse_invoice_response_debit_memo import ReverseInvoiceResponseDebitMemo

# TODO update the JSON string below
json = "{}"
# create an instance of ReverseInvoiceResponseDebitMemo from a JSON string
reverse_invoice_response_debit_memo_instance = ReverseInvoiceResponseDebitMemo.from_json(json)
# print the JSON string representation of the object
print(ReverseInvoiceResponseDebitMemo.to_json())

# convert the object into a dict
reverse_invoice_response_debit_memo_dict = reverse_invoice_response_debit_memo_instance.to_dict()
# create an instance of ReverseInvoiceResponseDebitMemo from a dict
reverse_invoice_response_debit_memo_from_dict = ReverseInvoiceResponseDebitMemo.from_dict(reverse_invoice_response_debit_memo_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


