# SignUpCreatePMPayPalECPayPalNativeEC


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**baid** | **str** | ID of a PayPal billing agreement, for example, I-1TJ3GAGG82Y9.  | [optional] 
**email** | **str** | Email address associated with the payment method. This field is only supported for PayPal payment methods and is required if you want to create any of the following PayPal payment methods:   - PayPal Express Checkout payment method    - PayPal Adaptive payment method   - PayPal Commerce Platform payment method | [optional] 

## Example

```python
from zuora_sdk.models.sign_up_create_pm_pay_pal_ec_pay_pal_native_ec import SignUpCreatePMPayPalECPayPalNativeEC

# TODO update the JSON string below
json = "{}"
# create an instance of SignUpCreatePMPayPalECPayPalNativeEC from a JSON string
sign_up_create_pm_pay_pal_ec_pay_pal_native_ec_instance = SignUpCreatePMPayPalECPayPalNativeEC.from_json(json)
# print the JSON string representation of the object
print(SignUpCreatePMPayPalECPayPalNativeEC.to_json())

# convert the object into a dict
sign_up_create_pm_pay_pal_ec_pay_pal_native_ec_dict = sign_up_create_pm_pay_pal_ec_pay_pal_native_ec_instance.to_dict()
# create an instance of SignUpCreatePMPayPalECPayPalNativeEC from a dict
sign_up_create_pm_pay_pal_ec_pay_pal_native_ec_from_dict = SignUpCreatePMPayPalECPayPalNativeEC.from_dict(sign_up_create_pm_pay_pal_ec_pay_pal_native_ec_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


