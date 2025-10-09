# CreatePaymentMethodGooglePayAdyenChase


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**google_payment_token** | **str** | This field is specific for setting up Google Pay for Adyen and Chase gateway integrations to specify the stringified Google Pay token. For more information, see [Set up Adyen Google Pay](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/L_Payment_Methods/Payment_Method_Types/Set_up_Adyen_Google_Pay) and [Set up Google Pay on Chase](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/L_Payment_Methods/Payment_Method_Types/Set_up_Google_Pay_on_Chase). | [optional] 

## Example

```python
from zuora_sdk.models.create_payment_method_google_pay_adyen_chase import CreatePaymentMethodGooglePayAdyenChase

# TODO update the JSON string below
json = "{}"
# create an instance of CreatePaymentMethodGooglePayAdyenChase from a JSON string
create_payment_method_google_pay_adyen_chase_instance = CreatePaymentMethodGooglePayAdyenChase.from_json(json)
# print the JSON string representation of the object
print(CreatePaymentMethodGooglePayAdyenChase.to_json())

# convert the object into a dict
create_payment_method_google_pay_adyen_chase_dict = create_payment_method_google_pay_adyen_chase_instance.to_dict()
# create an instance of CreatePaymentMethodGooglePayAdyenChase from a dict
create_payment_method_google_pay_adyen_chase_from_dict = CreatePaymentMethodGooglePayAdyenChase.from_dict(create_payment_method_google_pay_adyen_chase_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


