# PaymentProfile

Container for the payment profile settings of the subscription. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**payment_gateway_id** | **str** | Specifies by ID the payment gateway to be assigned to the subscription. | [optional] 
**payment_gateway_key** | **str** | Specifies by key the payment gateway to be assigned to the subscription. | [optional] 
**payment_method_id** | **str** | Specifies by ID the payment method to be assigned to the subscription. | [optional] 
**payment_method_key** | **str** | Specifies by key the payment method to be assigned to the subscription. | [optional] 
**clearing_existing_payment_gateway_id** | **bool** | Specifies whether the existing payment gateway should be cleared from the subscription. If set to &#x60;true&#x60;, the &#x60;paymentGatewayId&#x60; field is ignored.  | [optional] [default to False]
**clearing_existing_payment_method_id** | **bool** | Specifies whether the existing payment method should be cleared from the subscription. If set to &#x60;true&#x60;, the &#x60;paymentMethodId&#x60; field is ignored.  | [optional] [default to False]

## Example

```python
from zuora_sdk.models.payment_profile import PaymentProfile

# TODO update the JSON string below
json = "{}"
# create an instance of PaymentProfile from a JSON string
payment_profile_instance = PaymentProfile.from_json(json)
# print the JSON string representation of the object
print(PaymentProfile.to_json())

# convert the object into a dict
payment_profile_dict = payment_profile_instance.to_dict()
# create an instance of PaymentProfile from a dict
payment_profile_from_dict = PaymentProfile.from_dict(payment_profile_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


