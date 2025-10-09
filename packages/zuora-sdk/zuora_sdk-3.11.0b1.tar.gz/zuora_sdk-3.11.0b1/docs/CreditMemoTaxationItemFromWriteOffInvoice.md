# CreditMemoTaxationItemFromWriteOffInvoice


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** |  | [optional] 
**taxation_item_id** | **str** | The ID of the invoice item.  | [optional] 

## Example

```python
from zuora_sdk.models.credit_memo_taxation_item_from_write_off_invoice import CreditMemoTaxationItemFromWriteOffInvoice

# TODO update the JSON string below
json = "{}"
# create an instance of CreditMemoTaxationItemFromWriteOffInvoice from a JSON string
credit_memo_taxation_item_from_write_off_invoice_instance = CreditMemoTaxationItemFromWriteOffInvoice.from_json(json)
# print the JSON string representation of the object
print(CreditMemoTaxationItemFromWriteOffInvoice.to_json())

# convert the object into a dict
credit_memo_taxation_item_from_write_off_invoice_dict = credit_memo_taxation_item_from_write_off_invoice_instance.to_dict()
# create an instance of CreditMemoTaxationItemFromWriteOffInvoice from a dict
credit_memo_taxation_item_from_write_off_invoice_from_dict = CreditMemoTaxationItemFromWriteOffInvoice.from_dict(credit_memo_taxation_item_from_write_off_invoice_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


