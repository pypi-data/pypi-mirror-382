# CreatePaymentInvoiceApplicationItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The amount of the payment associated with the specific invoice or taxation item. | 
**invoice_item_id** | **str** | The ID of the specific invoice item.  | [optional] 
**tax_item_id** | **str** | The ID of the specific taxation item.  | [optional] 

## Example

```python
from zuora_sdk.models.create_payment_invoice_application_item import CreatePaymentInvoiceApplicationItem

# TODO update the JSON string below
json = "{}"
# create an instance of CreatePaymentInvoiceApplicationItem from a JSON string
create_payment_invoice_application_item_instance = CreatePaymentInvoiceApplicationItem.from_json(json)
# print the JSON string representation of the object
print(CreatePaymentInvoiceApplicationItem.to_json())

# convert the object into a dict
create_payment_invoice_application_item_dict = create_payment_invoice_application_item_instance.to_dict()
# create an instance of CreatePaymentInvoiceApplicationItem from a dict
create_payment_invoice_application_item_from_dict = CreatePaymentInvoiceApplicationItem.from_dict(create_payment_invoice_application_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


