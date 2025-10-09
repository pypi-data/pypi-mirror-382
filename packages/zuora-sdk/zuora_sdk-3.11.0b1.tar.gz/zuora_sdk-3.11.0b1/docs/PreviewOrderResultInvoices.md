# PreviewOrderResultInvoices


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** |  | [optional] 
**amount_without_tax** | **float** |  | [optional] 
**invoice_items** | [**List[InvoiceItemPreviewResult]**](InvoiceItemPreviewResult.md) |  | [optional] 
**target_date** | **date** |  | [optional] 
**tax_amount** | **float** |  | [optional] 

## Example

```python
from zuora_sdk.models.preview_order_result_invoices import PreviewOrderResultInvoices

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewOrderResultInvoices from a JSON string
preview_order_result_invoices_instance = PreviewOrderResultInvoices.from_json(json)
# print the JSON string representation of the object
print(PreviewOrderResultInvoices.to_json())

# convert the object into a dict
preview_order_result_invoices_dict = preview_order_result_invoices_instance.to_dict()
# create an instance of PreviewOrderResultInvoices from a dict
preview_order_result_invoices_from_dict = PreviewOrderResultInvoices.from_dict(preview_order_result_invoices_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


