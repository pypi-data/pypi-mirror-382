# GetPaymentMethodResponsePayPalForAccount


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**baid** | **str** | ID of a PayPal billing agreement. For example, I-1TJ3GAGG82Y9.  | [optional] 
**email** | **str** | Email address associated with the PayPal payment method.   | [optional] 
**preapproval_key** | **str** | The PayPal preapproval key.                  | [optional] 

## Example

```python
from zuora_sdk.models.get_payment_method_response_pay_pal_for_account import GetPaymentMethodResponsePayPalForAccount

# TODO update the JSON string below
json = "{}"
# create an instance of GetPaymentMethodResponsePayPalForAccount from a JSON string
get_payment_method_response_pay_pal_for_account_instance = GetPaymentMethodResponsePayPalForAccount.from_json(json)
# print the JSON string representation of the object
print(GetPaymentMethodResponsePayPalForAccount.to_json())

# convert the object into a dict
get_payment_method_response_pay_pal_for_account_dict = get_payment_method_response_pay_pal_for_account_instance.to_dict()
# create an instance of GetPaymentMethodResponsePayPalForAccount from a dict
get_payment_method_response_pay_pal_for_account_from_dict = GetPaymentMethodResponsePayPalForAccount.from_dict(get_payment_method_response_pay_pal_for_account_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


