# UnapplyPaymentInvoiceApplicationItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount of the payment that is unapplied from the specific invoice or taxation item. | 
**invoice_item_id** | **str** | The ID of the specific invoice item.  | [optional] 
**tax_item_id** | **str** | The ID of the specific taxation item.  | [optional] 

## Example

```python
from zuora_sdk.models.unapply_payment_invoice_application_item import UnapplyPaymentInvoiceApplicationItem

# TODO update the JSON string below
json = "{}"
# create an instance of UnapplyPaymentInvoiceApplicationItem from a JSON string
unapply_payment_invoice_application_item_instance = UnapplyPaymentInvoiceApplicationItem.from_json(json)
# print the JSON string representation of the object
print(UnapplyPaymentInvoiceApplicationItem.to_json())

# convert the object into a dict
unapply_payment_invoice_application_item_dict = unapply_payment_invoice_application_item_instance.to_dict()
# create an instance of UnapplyPaymentInvoiceApplicationItem from a dict
unapply_payment_invoice_application_item_from_dict = UnapplyPaymentInvoiceApplicationItem.from_dict(unapply_payment_invoice_application_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


