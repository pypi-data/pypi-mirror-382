# VerifyPaymentMethodRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**currency_code** | **str** | The currency used for payment method authorization.   | [optional] 
**gateway_options** | [**GatewayOptions**](GatewayOptions.md) |  | [optional] 
**payment_gateway_name** | **str** | The name of the payment gateway instance. If no value is specified for this field, the default payment gateway of the customer account will be used. | [optional] 
**security_code** | **str** | The CVV or CVV2 security code for the credit card or debit card. To ensure PCI compliance, the value of this field is not stored and cannot be queried. | [optional] 
**cryptogram** | **str** | Cryptogram value supplied by the token provider if DPAN or network scheme token is present  To ensure PCI compliance, this value is not stored and cannot be queried.  | [optional] 

## Example

```python
from zuora_sdk.models.verify_payment_method_request import VerifyPaymentMethodRequest

# TODO update the JSON string below
json = "{}"
# create an instance of VerifyPaymentMethodRequest from a JSON string
verify_payment_method_request_instance = VerifyPaymentMethodRequest.from_json(json)
# print the JSON string representation of the object
print(VerifyPaymentMethodRequest.to_json())

# convert the object into a dict
verify_payment_method_request_dict = verify_payment_method_request_instance.to_dict()
# create an instance of VerifyPaymentMethodRequest from a dict
verify_payment_method_request_from_dict = VerifyPaymentMethodRequest.from_dict(verify_payment_method_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


