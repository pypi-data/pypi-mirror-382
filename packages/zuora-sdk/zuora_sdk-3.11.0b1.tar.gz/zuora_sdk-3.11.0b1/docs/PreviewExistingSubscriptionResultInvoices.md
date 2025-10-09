# PreviewExistingSubscriptionResultInvoices


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**invoice_number** | **str** | The invoice number. | [optional] 
**amount** | **float** | Invoice amount. | [optional] 
**amount_without_tax** | **float** | Invoice amount minus tax. | [optional] 
**tax_amount** | **float** | The tax amount of the invoice. | [optional] 
**target_date** | **date** | Date through which to calculate charges if an invoice is generated, as yyyy-mm-dd. | [optional] 
**invoice_items** | [**List[PreviewExistingSubscriptionInvoiceItemResult]**](PreviewExistingSubscriptionInvoiceItemResult.md) | Container for invoice items. | [optional] 
**status** | **str** | The status of the invoice. | [optional] 
**is_from_existing_invoice** | **bool** | Indicates whether the invoice information is from an existing invoice. | [optional] 

## Example

```python
from zuora_sdk.models.preview_existing_subscription_result_invoices import PreviewExistingSubscriptionResultInvoices

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewExistingSubscriptionResultInvoices from a JSON string
preview_existing_subscription_result_invoices_instance = PreviewExistingSubscriptionResultInvoices.from_json(json)
# print the JSON string representation of the object
print(PreviewExistingSubscriptionResultInvoices.to_json())

# convert the object into a dict
preview_existing_subscription_result_invoices_dict = preview_existing_subscription_result_invoices_instance.to_dict()
# create an instance of PreviewExistingSubscriptionResultInvoices from a dict
preview_existing_subscription_result_invoices_from_dict = PreviewExistingSubscriptionResultInvoices.from_dict(preview_existing_subscription_result_invoices_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


