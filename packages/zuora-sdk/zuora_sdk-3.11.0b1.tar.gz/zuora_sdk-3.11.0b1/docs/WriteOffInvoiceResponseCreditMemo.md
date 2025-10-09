# WriteOffInvoiceResponseCreditMemo

Container for the credit memo that is automatically generated when writing off invoices.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the credit memo that is created when the invoice is written off.  | [optional] 

## Example

```python
from zuora_sdk.models.write_off_invoice_response_credit_memo import WriteOffInvoiceResponseCreditMemo

# TODO update the JSON string below
json = "{}"
# create an instance of WriteOffInvoiceResponseCreditMemo from a JSON string
write_off_invoice_response_credit_memo_instance = WriteOffInvoiceResponseCreditMemo.from_json(json)
# print the JSON string representation of the object
print(WriteOffInvoiceResponseCreditMemo.to_json())

# convert the object into a dict
write_off_invoice_response_credit_memo_dict = write_off_invoice_response_credit_memo_instance.to_dict()
# create an instance of WriteOffInvoiceResponseCreditMemo from a dict
write_off_invoice_response_credit_memo_from_dict = WriteOffInvoiceResponseCreditMemo.from_dict(write_off_invoice_response_credit_memo_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


