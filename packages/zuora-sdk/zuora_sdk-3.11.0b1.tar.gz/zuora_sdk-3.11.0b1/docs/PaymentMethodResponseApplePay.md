# PaymentMethodResponseApplePay


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**apple_bin** | **str** | This field is only available for Apple Pay payment methods.  | [optional] 
**apple_card_number** | **str** | This field is only available for Apple Pay payment methods.  | [optional] 
**apple_card_type** | **str** | This field is only available for Apple Pay payment methods.   For Apple Pay payment methods on Adyen, the first 100 characters of [paymentMethodVariant](https://docs.adyen.com/development-resources/paymentmethodvariant) returned from Adyen are stored in this field. | [optional] 
**apple_expiry_date** | **str** | This field is only available for Apple Pay payment methods.  | [optional] 
**apple_gateway_token** | **str** | This field is only available for Apple Pay payment methods.  | [optional] 

## Example

```python
from zuora_sdk.models.payment_method_response_apple_pay import PaymentMethodResponseApplePay

# TODO update the JSON string below
json = "{}"
# create an instance of PaymentMethodResponseApplePay from a JSON string
payment_method_response_apple_pay_instance = PaymentMethodResponseApplePay.from_json(json)
# print the JSON string representation of the object
print(PaymentMethodResponseApplePay.to_json())

# convert the object into a dict
payment_method_response_apple_pay_dict = payment_method_response_apple_pay_instance.to_dict()
# create an instance of PaymentMethodResponseApplePay from a dict
payment_method_response_apple_pay_from_dict = PaymentMethodResponseApplePay.from_dict(payment_method_response_apple_pay_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


