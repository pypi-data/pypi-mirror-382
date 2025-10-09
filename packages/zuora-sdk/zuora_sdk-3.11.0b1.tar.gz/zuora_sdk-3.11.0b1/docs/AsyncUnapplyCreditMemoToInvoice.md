# AsyncUnapplyCreditMemoToInvoice


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The credit memo amount to be unapplied from the invoice.  | 
**invoice_id** | **str** | The unique ID of the invoice that the credit memo is unapplied from.  | 

## Example

```python
from zuora_sdk.models.async_unapply_credit_memo_to_invoice import AsyncUnapplyCreditMemoToInvoice

# TODO update the JSON string below
json = "{}"
# create an instance of AsyncUnapplyCreditMemoToInvoice from a JSON string
async_unapply_credit_memo_to_invoice_instance = AsyncUnapplyCreditMemoToInvoice.from_json(json)
# print the JSON string representation of the object
print(AsyncUnapplyCreditMemoToInvoice.to_json())

# convert the object into a dict
async_unapply_credit_memo_to_invoice_dict = async_unapply_credit_memo_to_invoice_instance.to_dict()
# create an instance of AsyncUnapplyCreditMemoToInvoice from a dict
async_unapply_credit_memo_to_invoice_from_dict = AsyncUnapplyCreditMemoToInvoice.from_dict(async_unapply_credit_memo_to_invoice_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


