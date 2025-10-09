# CreatePaymentSessionInvoice


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**invoice_number** | **str** | The number of the invoice that the payment is applied to. For example, &#x60;INV00000001&#x60;.  | [optional] 

## Example

```python
from zuora_sdk.models.create_payment_session_invoice import CreatePaymentSessionInvoice

# TODO update the JSON string below
json = "{}"
# create an instance of CreatePaymentSessionInvoice from a JSON string
create_payment_session_invoice_instance = CreatePaymentSessionInvoice.from_json(json)
# print the JSON string representation of the object
print(CreatePaymentSessionInvoice.to_json())

# convert the object into a dict
create_payment_session_invoice_dict = create_payment_session_invoice_instance.to_dict()
# create an instance of CreatePaymentSessionInvoice from a dict
create_payment_session_invoice_from_dict = CreatePaymentSessionInvoice.from_dict(create_payment_session_invoice_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


