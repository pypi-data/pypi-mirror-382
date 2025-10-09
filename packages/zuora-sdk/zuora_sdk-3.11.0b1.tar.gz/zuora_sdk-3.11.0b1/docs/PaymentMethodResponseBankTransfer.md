# PaymentMethodResponseBankTransfer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**iban** | **str** | The International Bank Account Number used to create the SEPA payment method. The value is masked. | [optional] 
**account_number** | **str** | The number of the customer&#39;s bank account and it is masked.  | [optional] 
**bank_code** | **str** | The sort code or number that identifies the bank. This is also known as the sort code.          | [optional] 
**bank_transfer_type** | **str** | The type of the Bank Transfer payment method. For example, &#x60;SEPA&#x60;.  | [optional] 
**branch_code** | **str** | The branch code of the bank used for Direct Debit.            | [optional] 
**business_identification_code** | **str** | The BIC code used for SEPA. The value is masked.         | [optional] 
**identity_number** | **str** | The identity number of the customer.  | [optional] 
**bank_account_type** | [**PaymentMethodPADBankAccountType**](PaymentMethodPADBankAccountType.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.payment_method_response_bank_transfer import PaymentMethodResponseBankTransfer

# TODO update the JSON string below
json = "{}"
# create an instance of PaymentMethodResponseBankTransfer from a JSON string
payment_method_response_bank_transfer_instance = PaymentMethodResponseBankTransfer.from_json(json)
# print the JSON string representation of the object
print(PaymentMethodResponseBankTransfer.to_json())

# convert the object into a dict
payment_method_response_bank_transfer_dict = payment_method_response_bank_transfer_instance.to_dict()
# create an instance of PaymentMethodResponseBankTransfer from a dict
payment_method_response_bank_transfer_from_dict = PaymentMethodResponseBankTransfer.from_dict(payment_method_response_bank_transfer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


