# CreatePaymentMethodBankTransferAccountHolderInfo

This container field is required for the following bank transfer payment methods. The nested `accountHolderName` field is required.   - Direct Debit NZ (`Becsnz`)   - Single Euro Payments Area (`SEPA`)   - Direct Debit UK (`Bacs`)   - Denmark Direct Debit (`Betalingsservice`)   - Sweden Direct Debit (`Autogiro`)   - Canadian Pre-Authorized Debit (`PAD`)

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_holder_name** | **str** | Required.  The full name of the bank account holder.  | [optional] 
**address_line1** | **str** | The first line of the address for the account holder.   This field is required for SEPA Direct Debit payment methods on Stripe v2 for [certain countries](https://stripe.com/docs/payments/sepa-debit/set-up-payment?platform&#x3D;web#web-submit-payment-method). | [optional] 
**address_line2** | **str** | The second line of the address for the account holder.   | [optional] 
**city** | **str** | The city where the account holder stays.   It is recommended to provide the city and country information when creating a payment method. The information will be used to process payments. If the information is not provided during payment method creation, the city and country data will be missing during payment processing. | [optional] 
**country** | **str** | The country where the account holder stays.   This field is required for SEPA payment methods on Stripe v2 for [certain countries](https://stripe.com/docs/payments/sepa-debit/set-up-payment?platform&#x3D;web#web-submit-payment-method). | [optional] 
**email** | **str** | The email address of the account holder.  | [optional] 
**first_name** | **str** | The first name of the account holder.  | [optional] 
**last_name** | **str** | The last name of the account holder.  | [optional] 
**phone** | **str** | The phone number of the account holder.  | [optional] 
**state** | **str** | The state where the account holder stays.  | [optional] 
**zip_code** | **str** | The zip code for the address of the account holder.  | [optional] 

## Example

```python
from zuora_sdk.models.create_payment_method_bank_transfer_account_holder_info import CreatePaymentMethodBankTransferAccountHolderInfo

# TODO update the JSON string below
json = "{}"
# create an instance of CreatePaymentMethodBankTransferAccountHolderInfo from a JSON string
create_payment_method_bank_transfer_account_holder_info_instance = CreatePaymentMethodBankTransferAccountHolderInfo.from_json(json)
# print the JSON string representation of the object
print(CreatePaymentMethodBankTransferAccountHolderInfo.to_json())

# convert the object into a dict
create_payment_method_bank_transfer_account_holder_info_dict = create_payment_method_bank_transfer_account_holder_info_instance.to_dict()
# create an instance of CreatePaymentMethodBankTransferAccountHolderInfo from a dict
create_payment_method_bank_transfer_account_holder_info_from_dict = CreatePaymentMethodBankTransferAccountHolderInfo.from_dict(create_payment_method_bank_transfer_account_holder_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


