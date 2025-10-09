# GetPaymentMethodResponseCreditCardForAccount


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**card_number** | **str** | The masked credit card number.  When &#x60;cardNumber&#x60; is &#x60;null&#x60;, the following fields will not be returned:   - &#x60;expirationMonth&#x60;   - &#x60;expirationYear&#x60;   - &#x60;accountHolderInfo&#x60;  | [optional] 
**expiration_month** | **int** | One or two digits expiration month (1-12).  | [optional] 
**expiration_year** | **int** | Four-digit expiration year.  | [optional] 
**security_code** | **str** | The CVV or CVV2 security code for the credit card or debit card.             Only required if changing expirationMonth, expirationYear, or cardHolderName.             To ensure PCI compliance, this value isn&#39;&#39;t stored and can&#39;&#39;t be queried.   | [optional] 

## Example

```python
from zuora_sdk.models.get_payment_method_response_credit_card_for_account import GetPaymentMethodResponseCreditCardForAccount

# TODO update the JSON string below
json = "{}"
# create an instance of GetPaymentMethodResponseCreditCardForAccount from a JSON string
get_payment_method_response_credit_card_for_account_instance = GetPaymentMethodResponseCreditCardForAccount.from_json(json)
# print the JSON string representation of the object
print(GetPaymentMethodResponseCreditCardForAccount.to_json())

# convert the object into a dict
get_payment_method_response_credit_card_for_account_dict = get_payment_method_response_credit_card_for_account_instance.to_dict()
# create an instance of GetPaymentMethodResponseCreditCardForAccount from a dict
get_payment_method_response_credit_card_for_account_from_dict = GetPaymentMethodResponseCreditCardForAccount.from_dict(get_payment_method_response_credit_card_for_account_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


