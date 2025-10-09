# CreateInvoiceCollectInvoices


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**invoice_amount** | **decimal.Decimal** | The amount of the invoice.  | [optional] 
**invoice_id** | **str** | The ID of the invoice.  | [optional] 
**invoice_number** | **str** | The unique identification number of the invoice.  | [optional] 

## Example

```python
from zuora_sdk.models.create_invoice_collect_invoices import CreateInvoiceCollectInvoices

# TODO update the JSON string below
json = "{}"
# create an instance of CreateInvoiceCollectInvoices from a JSON string
create_invoice_collect_invoices_instance = CreateInvoiceCollectInvoices.from_json(json)
# print the JSON string representation of the object
print(CreateInvoiceCollectInvoices.to_json())

# convert the object into a dict
create_invoice_collect_invoices_dict = create_invoice_collect_invoices_instance.to_dict()
# create an instance of CreateInvoiceCollectInvoices from a dict
create_invoice_collect_invoices_from_dict = CreateInvoiceCollectInvoices.from_dict(create_invoice_collect_invoices_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


