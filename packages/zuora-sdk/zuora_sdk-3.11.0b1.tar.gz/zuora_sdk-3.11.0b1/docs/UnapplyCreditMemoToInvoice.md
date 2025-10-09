# UnapplyCreditMemoToInvoice


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The credit memo amount to be unapplied from the invoice.  | 
**invoice_id** | **str** | The unique ID of the invoice that the credit memo is unapplied from.  | 
**items** | [**List[UnapplyCreditMemoItemToInvoiceItem]**](UnapplyCreditMemoItemToInvoiceItem.md) | Container for items. The maximum number of items is 1,000.  | [optional] 

## Example

```python
from zuora_sdk.models.unapply_credit_memo_to_invoice import UnapplyCreditMemoToInvoice

# TODO update the JSON string below
json = "{}"
# create an instance of UnapplyCreditMemoToInvoice from a JSON string
unapply_credit_memo_to_invoice_instance = UnapplyCreditMemoToInvoice.from_json(json)
# print the JSON string representation of the object
print(UnapplyCreditMemoToInvoice.to_json())

# convert the object into a dict
unapply_credit_memo_to_invoice_dict = unapply_credit_memo_to_invoice_instance.to_dict()
# create an instance of UnapplyCreditMemoToInvoice from a dict
unapply_credit_memo_to_invoice_from_dict = UnapplyCreditMemoToInvoice.from_dict(unapply_credit_memo_to_invoice_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


