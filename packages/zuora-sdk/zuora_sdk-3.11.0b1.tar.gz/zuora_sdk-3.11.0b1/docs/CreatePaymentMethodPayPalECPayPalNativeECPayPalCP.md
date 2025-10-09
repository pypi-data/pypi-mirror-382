# CreatePaymentMethodPayPalECPayPalNativeECPayPalCP


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**baid** | **str** | ID of a PayPal billing agreement. For example, I-1TJ3GAGG82Y9.  | [optional] 
**email** | **str** | Email address associated with the payment method. This field is supported for the following payment methods:   - PayPal payment methods. This field is required for creating any of the following PayPal payment methods.     - PayPal Express Checkout     - PayPal Adaptive     - PayPal Commerce Platform   - Apple Pay and Google Pay payment methods on Adyen v2.0. This field will be passed to Adyen as &#x60;shopperEmail&#x60;. | [optional] 

## Example

```python
from zuora_sdk.models.create_payment_method_pay_pal_ec_pay_pal_native_ec_pay_pal_cp import CreatePaymentMethodPayPalECPayPalNativeECPayPalCP

# TODO update the JSON string below
json = "{}"
# create an instance of CreatePaymentMethodPayPalECPayPalNativeECPayPalCP from a JSON string
create_payment_method_pay_pal_ec_pay_pal_native_ec_pay_pal_cp_instance = CreatePaymentMethodPayPalECPayPalNativeECPayPalCP.from_json(json)
# print the JSON string representation of the object
print(CreatePaymentMethodPayPalECPayPalNativeECPayPalCP.to_json())

# convert the object into a dict
create_payment_method_pay_pal_ec_pay_pal_native_ec_pay_pal_cp_dict = create_payment_method_pay_pal_ec_pay_pal_native_ec_pay_pal_cp_instance.to_dict()
# create an instance of CreatePaymentMethodPayPalECPayPalNativeECPayPalCP from a dict
create_payment_method_pay_pal_ec_pay_pal_native_ec_pay_pal_cp_from_dict = CreatePaymentMethodPayPalECPayPalNativeECPayPalCP.from_dict(create_payment_method_pay_pal_ec_pay_pal_native_ec_pay_pal_cp_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


