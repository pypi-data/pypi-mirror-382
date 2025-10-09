# ReverseInvoiceResponseCreditMemo

Container for the credit memo that is automatically generated when during the invoice reversal.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the credit memo. | [optional] 

## Example

```python
from zuora_sdk.models.reverse_invoice_response_credit_memo import ReverseInvoiceResponseCreditMemo

# TODO update the JSON string below
json = "{}"
# create an instance of ReverseInvoiceResponseCreditMemo from a JSON string
reverse_invoice_response_credit_memo_instance = ReverseInvoiceResponseCreditMemo.from_json(json)
# print the JSON string representation of the object
print(ReverseInvoiceResponseCreditMemo.to_json())

# convert the object into a dict
reverse_invoice_response_credit_memo_dict = reverse_invoice_response_credit_memo_instance.to_dict()
# create an instance of ReverseInvoiceResponseCreditMemo from a dict
reverse_invoice_response_credit_memo_from_dict = ReverseInvoiceResponseCreditMemo.from_dict(reverse_invoice_response_credit_memo_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


