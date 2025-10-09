# GetPaymentMethodResponseGooglePayForAccount


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
from zuora_sdk.models.get_payment_method_response_google_pay_for_account import GetPaymentMethodResponseGooglePayForAccount

# TODO update the JSON string below
json = "{}"
# create an instance of GetPaymentMethodResponseGooglePayForAccount from a JSON string
get_payment_method_response_google_pay_for_account_instance = GetPaymentMethodResponseGooglePayForAccount.from_json(json)
# print the JSON string representation of the object
print(GetPaymentMethodResponseGooglePayForAccount.to_json())

# convert the object into a dict
get_payment_method_response_google_pay_for_account_dict = get_payment_method_response_google_pay_for_account_instance.to_dict()
# create an instance of GetPaymentMethodResponseGooglePayForAccount from a dict
get_payment_method_response_google_pay_for_account_from_dict = GetPaymentMethodResponseGooglePayForAccount.from_dict(get_payment_method_response_google_pay_for_account_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


