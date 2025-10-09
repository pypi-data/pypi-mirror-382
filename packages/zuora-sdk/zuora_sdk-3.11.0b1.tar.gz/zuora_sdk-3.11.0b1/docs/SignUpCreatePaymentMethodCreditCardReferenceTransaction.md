# SignUpCreatePaymentMethodCreditCardReferenceTransaction


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**second_token_id** | **str** | The second token id of CreditCardReferenceTransaction.  | [optional] 
**token_id** | **str** | The token id of payment method, required field of CreditCardReferenceTransaction type. | [optional] 

## Example

```python
from zuora_sdk.models.sign_up_create_payment_method_credit_card_reference_transaction import SignUpCreatePaymentMethodCreditCardReferenceTransaction

# TODO update the JSON string below
json = "{}"
# create an instance of SignUpCreatePaymentMethodCreditCardReferenceTransaction from a JSON string
sign_up_create_payment_method_credit_card_reference_transaction_instance = SignUpCreatePaymentMethodCreditCardReferenceTransaction.from_json(json)
# print the JSON string representation of the object
print(SignUpCreatePaymentMethodCreditCardReferenceTransaction.to_json())

# convert the object into a dict
sign_up_create_payment_method_credit_card_reference_transaction_dict = sign_up_create_payment_method_credit_card_reference_transaction_instance.to_dict()
# create an instance of SignUpCreatePaymentMethodCreditCardReferenceTransaction from a dict
sign_up_create_payment_method_credit_card_reference_transaction_from_dict = SignUpCreatePaymentMethodCreditCardReferenceTransaction.from_dict(sign_up_create_payment_method_credit_card_reference_transaction_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


