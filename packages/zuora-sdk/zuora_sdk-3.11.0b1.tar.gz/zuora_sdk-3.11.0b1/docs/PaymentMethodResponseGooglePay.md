# PaymentMethodResponseGooglePay


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**google_bin** | **str** | This field is only available for Google Pay payment methods.  | [optional] 
**google_card_number** | **str** | This field is only available for Google Pay payment methods.  | [optional] 
**google_card_type** | **str** | This field is only available for Google Pay payment methods.   For Google Pay payment methods on Adyen, the first 100 characters of [paymentMethodVariant](https://docs.adyen.com/development-resources/paymentmethodvariant) returned from Adyen are stored in this field. | [optional] 
**google_expiry_date** | **str** | This field is only available for Google Pay payment methods.  | [optional] 
**google_gateway_token** | **str** | This field is only available for Google Pay payment methods.  | [optional] 

## Example

```python
from zuora_sdk.models.payment_method_response_google_pay import PaymentMethodResponseGooglePay

# TODO update the JSON string below
json = "{}"
# create an instance of PaymentMethodResponseGooglePay from a JSON string
payment_method_response_google_pay_instance = PaymentMethodResponseGooglePay.from_json(json)
# print the JSON string representation of the object
print(PaymentMethodResponseGooglePay.to_json())

# convert the object into a dict
payment_method_response_google_pay_dict = payment_method_response_google_pay_instance.to_dict()
# create an instance of PaymentMethodResponseGooglePay from a dict
payment_method_response_google_pay_from_dict = PaymentMethodResponseGooglePay.from_dict(payment_method_response_google_pay_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


