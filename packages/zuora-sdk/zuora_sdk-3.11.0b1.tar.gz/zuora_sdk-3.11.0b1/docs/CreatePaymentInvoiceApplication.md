# CreatePaymentInvoiceApplication


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount of the payment associated with the invoice. This amount must be equal to or lesser than the balance of the invoice. | 
**invoice_id** | **str** | The unique ID of the invoice that the payment is created on. The balance of the invoice specified must not be &#x60;0&#x60;. | [optional] 
**invoice_number** | **str** |  | [optional] 
**items** | [**List[CreatePaymentInvoiceApplicationItem]**](CreatePaymentInvoiceApplicationItem.md) | Container for invoice items. The maximum number of items is 1,000.   **Note:** This field is only available if you have the [Invoice Item Settlement](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement/C_Invoice_Item_Settlement) feature enabled. Invoice Item Settlement must be used together with other Invoice Settlement features (Unapplied Payments, and Credit and Debit memos).  If you wish to enable Invoice Settlement, see [Invoice Settlement Enablement and Checklist Guide](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement/Invoice_Settlement_Migration_Checklist_and_Guide) for more information. | [optional] 

## Example

```python
from zuora_sdk.models.create_payment_invoice_application import CreatePaymentInvoiceApplication

# TODO update the JSON string below
json = "{}"
# create an instance of CreatePaymentInvoiceApplication from a JSON string
create_payment_invoice_application_instance = CreatePaymentInvoiceApplication.from_json(json)
# print the JSON string representation of the object
print(CreatePaymentInvoiceApplication.to_json())

# convert the object into a dict
create_payment_invoice_application_dict = create_payment_invoice_application_instance.to_dict()
# create an instance of CreatePaymentInvoiceApplication from a dict
create_payment_invoice_application_from_dict = CreatePaymentInvoiceApplication.from_dict(create_payment_invoice_application_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


