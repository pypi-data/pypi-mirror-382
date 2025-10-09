# CreatePaymentMethodApplePayAdyen


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**apple_payment_data** | **str** | This field is specific for setting up Apple Pay for Adyen to include payload with Apple Pay token or Apple payment data. This information should be stringified. For more information, see [Set up Adyen Apple Pay](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/L_Payment_Methods/Payment_Method_Types/Apple_Pay_on_Web/Set_up_Adyen_Apple_Pay). | [optional] 

## Example

```python
from zuora_sdk.models.create_payment_method_apple_pay_adyen import CreatePaymentMethodApplePayAdyen

# TODO update the JSON string below
json = "{}"
# create an instance of CreatePaymentMethodApplePayAdyen from a JSON string
create_payment_method_apple_pay_adyen_instance = CreatePaymentMethodApplePayAdyen.from_json(json)
# print the JSON string representation of the object
print(CreatePaymentMethodApplePayAdyen.to_json())

# convert the object into a dict
create_payment_method_apple_pay_adyen_dict = create_payment_method_apple_pay_adyen_instance.to_dict()
# create an instance of CreatePaymentMethodApplePayAdyen from a dict
create_payment_method_apple_pay_adyen_from_dict = CreatePaymentMethodApplePayAdyen.from_dict(create_payment_method_apple_pay_adyen_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


