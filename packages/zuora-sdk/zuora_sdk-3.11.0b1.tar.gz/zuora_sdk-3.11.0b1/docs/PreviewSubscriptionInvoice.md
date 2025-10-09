# PreviewSubscriptionInvoice

Container for invoices.    **Note:** This field is only available if you set the Zuora REST API minor version to 207.0 or later in the request header. Also, the response structure is changed and the following invoice related response fields are moved to this **invoice** container:       * amount    * amountWithoutTax    * taxAmount    * invoiceItems    * targetDate 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | Invoice amount. | [optional] 
**amount_without_tax** | **float** | Invoice amount minus tax.  | [optional] 
**invoice_items** | [**List[PreviewSubscriptionInvoiceItem]**](PreviewSubscriptionInvoiceItem.md) | Container for invoice items.  | [optional] 
**target_date** | **str** | Date through which to calculate charges if an invoice is generated, as yyyy-mm-dd. Default is current date.   **Note:** This field is only available if you set the Zuora REST API minor version to 207.0 or later in the request header. See [Zuora REST API Versions](https://www.zuora.com/developer/api-references/api/overview/#section/API-Versions) for more information. | [optional] 
**tax_amount** | **float** | The tax amount of the invoice.  | [optional] 

## Example

```python
from zuora_sdk.models.preview_subscription_invoice import PreviewSubscriptionInvoice

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewSubscriptionInvoice from a JSON string
preview_subscription_invoice_instance = PreviewSubscriptionInvoice.from_json(json)
# print the JSON string representation of the object
print(PreviewSubscriptionInvoice.to_json())

# convert the object into a dict
preview_subscription_invoice_dict = preview_subscription_invoice_instance.to_dict()
# create an instance of PreviewSubscriptionInvoice from a dict
preview_subscription_invoice_from_dict = PreviewSubscriptionInvoice.from_dict(preview_subscription_invoice_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


