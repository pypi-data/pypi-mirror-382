# SignUpCreatePaymentMethodCommon


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_key** | **str** | Internal ID of the customer account that will own the payment method.  | [optional] 
**auth_gateway** | **str** | Internal ID of the payment gateway that Zuora will use to authorize the payments that are made with the payment method.   If you do not set this field, Zuora will use one of the following payment gateways instead:   * The default payment gateway of the customer account that owns the payment method, if the &#x60;accountKey&#x60; field is set.  * The default payment gateway of your Zuora tenant, if the &#x60;accountKey&#x60; field is not set. | [optional] 
**ip_address** | **str** | The IPv4 or IPv6 information of the user when the payment method is created or updated. Some gateways use this field for fraud prevention. If this field is passed to Zuora, Zuora directly passes it to gateways.    If the IP address length is beyond 45 characters, a validation error occurs. | [optional] 
**make_default** | **bool** | Specifies whether the payment method will be the default payment method of the customer account that owns the payment method. Only applicable if the &#x60;accountKey&#x60; field is set. | [optional] [default to False]

## Example

```python
from zuora_sdk.models.sign_up_create_payment_method_common import SignUpCreatePaymentMethodCommon

# TODO update the JSON string below
json = "{}"
# create an instance of SignUpCreatePaymentMethodCommon from a JSON string
sign_up_create_payment_method_common_instance = SignUpCreatePaymentMethodCommon.from_json(json)
# print the JSON string representation of the object
print(SignUpCreatePaymentMethodCommon.to_json())

# convert the object into a dict
sign_up_create_payment_method_common_dict = sign_up_create_payment_method_common_instance.to_dict()
# create an instance of SignUpCreatePaymentMethodCommon from a dict
sign_up_create_payment_method_common_from_dict = SignUpCreatePaymentMethodCommon.from_dict(sign_up_create_payment_method_common_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


