# ApplyPaymentInvoiceApplicationItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount of the payment that is applied to the specific invoice or taxation item. | 
**invoice_item_id** | **str** | The ID of the specific invoice item.  | [optional] 
**tax_item_id** | **str** | The ID of the specific taxation item.  | [optional] 

## Example

```python
from zuora_sdk.models.apply_payment_invoice_application_item import ApplyPaymentInvoiceApplicationItem

# TODO update the JSON string below
json = "{}"
# create an instance of ApplyPaymentInvoiceApplicationItem from a JSON string
apply_payment_invoice_application_item_instance = ApplyPaymentInvoiceApplicationItem.from_json(json)
# print the JSON string representation of the object
print(ApplyPaymentInvoiceApplicationItem.to_json())

# convert the object into a dict
apply_payment_invoice_application_item_dict = apply_payment_invoice_application_item_instance.to_dict()
# create an instance of ApplyPaymentInvoiceApplicationItem from a dict
apply_payment_invoice_application_item_from_dict = ApplyPaymentInvoiceApplicationItem.from_dict(apply_payment_invoice_application_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


