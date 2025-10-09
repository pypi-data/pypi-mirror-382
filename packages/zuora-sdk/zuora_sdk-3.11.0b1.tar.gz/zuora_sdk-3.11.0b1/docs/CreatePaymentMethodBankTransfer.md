# CreatePaymentMethodBankTransfer


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**iban** | **str** | The International Bank Account Number. This field is required if the &#x60;type&#x60; field is set to &#x60;SEPA&#x60;. | [optional] 
**account_holder_info** | [**CreatePaymentMethodBankTransferAccountHolderInfo**](CreatePaymentMethodBankTransferAccountHolderInfo.md) |  | [optional] 
**account_number** | **str** | The number of the customer&#39;s bank account. This field is required for the following bank transfer payment methods:   - Direct Entry AU (&#x60;Becs&#x60;)   - Direct Debit NZ (&#x60;Becsnz&#x60;)   - Direct Debit UK (&#x60;Bacs&#x60;)   - Denmark Direct Debit (&#x60;Betalingsservice&#x60;)   - Sweden Direct Debit (&#x60;Autogiro&#x60;)   - Canadian Pre-Authorized Debit (&#x60;PAD&#x60;) | [optional] 
**account_mask_number** | **str** | The masked account number of the payment method. | [optional] 
**bank_code** | **str** | The sort code or number that identifies the bank. This is also known as the sort code. This field is required for the following bank transfer payment methods:   - Direct Debit UK (&#x60;Bacs&#x60;)   - Denmark Direct Debit (&#x60;Betalingsservice&#x60;)   - Direct Debit NZ (&#x60;Becsnz&#x60;)   - Canadian Pre-Authorized Debit (&#x60;PAD&#x60;) | [optional] 
**branch_code** | **str** | The branch code of the bank used for direct debit. This field is required for the following bank transfer payment methods:   - Sweden Direct Debit (&#x60;Autogiro&#x60;)   - Direct Entry AU (&#x60;Becs&#x60;)   - Direct Debit NZ (&#x60;Becsnz&#x60;)   - Canadian Pre-Authorized Debit (&#x60;PAD&#x60;) | [optional] 
**business_identification_code** | **str** | The BIC code used for SEPA.  | [optional] 
**currency_code** | **str** | The currency used for payment method authorization.   If this field is not specified, &#x60;currency&#x60; specified for the account is used for payment method authorization. If no currency is specified for the account, the default currency of the account is then used. | [optional] 
**identity_number** | **str** | The identity number of the customer. This field is required for the following bank transfer payment methods:   - Denmark Direct Debit (&#x60;Betalingsservice&#x60;)   - Sweden Direct Debit (&#x60;Autogiro&#x60;) | [optional] 

## Example

```python
from zuora_sdk.models.create_payment_method_bank_transfer import CreatePaymentMethodBankTransfer

# TODO update the JSON string below
json = "{}"
# create an instance of CreatePaymentMethodBankTransfer from a JSON string
create_payment_method_bank_transfer_instance = CreatePaymentMethodBankTransfer.from_json(json)
# print the JSON string representation of the object
print(CreatePaymentMethodBankTransfer.to_json())

# convert the object into a dict
create_payment_method_bank_transfer_dict = create_payment_method_bank_transfer_instance.to_dict()
# create an instance of CreatePaymentMethodBankTransfer from a dict
create_payment_method_bank_transfer_from_dict = CreatePaymentMethodBankTransfer.from_dict(create_payment_method_bank_transfer_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


