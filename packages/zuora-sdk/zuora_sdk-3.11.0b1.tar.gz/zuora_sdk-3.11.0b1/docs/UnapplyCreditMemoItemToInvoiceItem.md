# UnapplyCreditMemoItemToInvoiceItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount that is unapplied from the specific item.   | 
**credit_memo_item_id** | **str** | The ID of the credit memo item.  | [optional] 
**credit_tax_item_id** | **str** | The ID of the credit memo taxation item.  | [optional] 
**invoice_item_id** | **str** | The ID of the invoice item that the credit memo item is unapplied from.  | [optional] 
**tax_item_id** | **str** | The ID of the invoice taxation item that the credit memo taxation item is unapplied from. | [optional] 

## Example

```python
from zuora_sdk.models.unapply_credit_memo_item_to_invoice_item import UnapplyCreditMemoItemToInvoiceItem

# TODO update the JSON string below
json = "{}"
# create an instance of UnapplyCreditMemoItemToInvoiceItem from a JSON string
unapply_credit_memo_item_to_invoice_item_instance = UnapplyCreditMemoItemToInvoiceItem.from_json(json)
# print the JSON string representation of the object
print(UnapplyCreditMemoItemToInvoiceItem.to_json())

# convert the object into a dict
unapply_credit_memo_item_to_invoice_item_dict = unapply_credit_memo_item_to_invoice_item_instance.to_dict()
# create an instance of UnapplyCreditMemoItemToInvoiceItem from a dict
unapply_credit_memo_item_to_invoice_item_from_dict = UnapplyCreditMemoItemToInvoiceItem.from_dict(unapply_credit_memo_item_to_invoice_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


