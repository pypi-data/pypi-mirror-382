# PaymentMethodResponsePayPal


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**baid** | **str** | ID of a PayPal billing agreement. For example, I-1TJ3GAGG82Y9.  | [optional] 
**email** | **str** | Email address associated with the PayPal payment method.   | [optional] 
**preapproval_key** | **str** | The PayPal preapproval key.  | [optional] 

## Example

```python
from zuora_sdk.models.payment_method_response_pay_pal import PaymentMethodResponsePayPal

# TODO update the JSON string below
json = "{}"
# create an instance of PaymentMethodResponsePayPal from a JSON string
payment_method_response_pay_pal_instance = PaymentMethodResponsePayPal.from_json(json)
# print the JSON string representation of the object
print(PaymentMethodResponsePayPal.to_json())

# convert the object into a dict
payment_method_response_pay_pal_dict = payment_method_response_pay_pal_instance.to_dict()
# create an instance of PaymentMethodResponsePayPal from a dict
payment_method_response_pay_pal_from_dict = PaymentMethodResponsePayPal.from_dict(payment_method_response_pay_pal_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


