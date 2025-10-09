# ApplyCreditMemoToInvoice


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The credit memo amount to be applied to the invoice.  | 
**invoice_id** | **str** | The unique ID of the invoice that the credit memo is applied to.  | 
**items** | [**List[ApplyCreditMemoItemToInvoiceItem]**](ApplyCreditMemoItemToInvoiceItem.md) | Container for items. The maximum number of items is 1,000.   If &#x60;creditMemoItemId&#x60; is the source, then it should be accompanied by a target &#x60;invoiceItemId&#x60;.   If &#x60;creditTaxItemId&#x60; is the source, then it should be accompanied by a target &#x60;taxItemId&#x60;. | [optional] 

## Example

```python
from zuora_sdk.models.apply_credit_memo_to_invoice import ApplyCreditMemoToInvoice

# TODO update the JSON string below
json = "{}"
# create an instance of ApplyCreditMemoToInvoice from a JSON string
apply_credit_memo_to_invoice_instance = ApplyCreditMemoToInvoice.from_json(json)
# print the JSON string representation of the object
print(ApplyCreditMemoToInvoice.to_json())

# convert the object into a dict
apply_credit_memo_to_invoice_dict = apply_credit_memo_to_invoice_instance.to_dict()
# create an instance of ApplyCreditMemoToInvoice from a dict
apply_credit_memo_to_invoice_from_dict = ApplyCreditMemoToInvoice.from_dict(apply_credit_memo_to_invoice_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


