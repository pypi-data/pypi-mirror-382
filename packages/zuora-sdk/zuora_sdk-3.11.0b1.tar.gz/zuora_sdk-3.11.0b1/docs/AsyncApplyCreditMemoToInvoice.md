# AsyncApplyCreditMemoToInvoice


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The credit memo amount to be applied to the invoice.  | 
**invoice_id** | **str** | The unique ID of the invoice that the credit memo is applied to.  | 

## Example

```python
from zuora_sdk.models.async_apply_credit_memo_to_invoice import AsyncApplyCreditMemoToInvoice

# TODO update the JSON string below
json = "{}"
# create an instance of AsyncApplyCreditMemoToInvoice from a JSON string
async_apply_credit_memo_to_invoice_instance = AsyncApplyCreditMemoToInvoice.from_json(json)
# print the JSON string representation of the object
print(AsyncApplyCreditMemoToInvoice.to_json())

# convert the object into a dict
async_apply_credit_memo_to_invoice_dict = async_apply_credit_memo_to_invoice_instance.to_dict()
# create an instance of AsyncApplyCreditMemoToInvoice from a dict
async_apply_credit_memo_to_invoice_from_dict = AsyncApplyCreditMemoToInvoice.from_dict(async_apply_credit_memo_to_invoice_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


