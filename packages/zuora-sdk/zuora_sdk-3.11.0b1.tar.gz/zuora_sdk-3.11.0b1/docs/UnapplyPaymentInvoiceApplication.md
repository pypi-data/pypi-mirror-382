# UnapplyPaymentInvoiceApplication


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount of the payment that is unapplied from the invoice.  | 
**invoice_id** | **str** | The unique ID of the invoice that the payment is unapplied from.  | [optional] 
**invoice_number** | **str** | The number of the invoice that the payment is unapplied from. For example, &#x60;INV00000001&#x60;.    **Note:** When both the &#x60;invoiceNumber&#x60; and &#x60;invoiceId&#x60; fields are specified, the two fields must match with each other. | [optional] 
**items** | [**List[UnapplyPaymentInvoiceApplicationItem]**](UnapplyPaymentInvoiceApplicationItem.md) | Container for invoice items. The maximum number of items is 1,000.   **Note:** This field is only available if you have the [Invoice Item Settlement](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement/C_Invoice_Item_Settlement) feature enabled. Invoice Item Settlement must be used together with other Invoice Settlement features (Unapplied Payments, and Credit and Debit memos).  If you wish to enable Invoice Settlement, see [Invoice Settlement Enablement and Checklist Guide](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement/Invoice_Settlement_Migration_Checklist_and_Guide) for more information. | [optional] 

## Example

```python
from zuora_sdk.models.unapply_payment_invoice_application import UnapplyPaymentInvoiceApplication

# TODO update the JSON string below
json = "{}"
# create an instance of UnapplyPaymentInvoiceApplication from a JSON string
unapply_payment_invoice_application_instance = UnapplyPaymentInvoiceApplication.from_json(json)
# print the JSON string representation of the object
print(UnapplyPaymentInvoiceApplication.to_json())

# convert the object into a dict
unapply_payment_invoice_application_dict = unapply_payment_invoice_application_instance.to_dict()
# create an instance of UnapplyPaymentInvoiceApplication from a dict
unapply_payment_invoice_application_from_dict = UnapplyPaymentInvoiceApplication.from_dict(unapply_payment_invoice_application_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


