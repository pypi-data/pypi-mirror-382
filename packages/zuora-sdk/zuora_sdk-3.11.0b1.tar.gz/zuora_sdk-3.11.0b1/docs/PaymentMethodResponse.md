# PaymentMethodResponse


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
**bank_account_type** | [**PaymentMethodACHBankAccountType**](PaymentMethodACHBankAccountType.md) |  | [optional] 
**bank_aba_code** | **str** | The nine-digit routing number or ABA number used by banks. This field is only required if the &#x60;type&#x60; field is set to &#x60;ACH&#x60;.  | [optional] 
**bank_account_name** | **str** | The name of the account holder, which can be either a person or a company. This field is only required if the &#x60;type&#x60; field is set to &#x60;ACH&#x60;.  | [optional] 
**bank_account_number** | **str** | The bank account number associated with the ACH payment. This field is only required if the &#x60;type&#x60; field is set to &#x60;ACH&#x60;. However, for creating tokenized ACH payment methods on Stripe v2, this field is optional if the &#x60;tokens&#x60; and &#x60;bankAccountMaskNumber&#x60; fields are specified.  | [optional] 
**bank_account_mask_number** | **str** | The masked bank account number associated with the ACH payment. This field is only required if the ACH payment method is created using tokens.  | [optional] 
**bank_name** | **str** | The name of the bank where the ACH payment account is held. This field is only required if the &#x60;type&#x60; field is set to &#x60;ACH&#x60;.  When creating an ACH payment method on Adyen, this field is required by Zuora but it is not required by Adyen. To create the ACH payment method successfully, specify a real value for this field if you can. If it is not possible to get the real value for it, specify a dummy value.  | [optional] 
**card_number** | **str** | The masked credit card number.  When &#x60;cardNumber&#x60; is &#x60;null&#x60;, the following fields will not be returned:   - &#x60;expirationMonth&#x60;   - &#x60;expirationYear&#x60;   - &#x60;accountHolderInfo&#x60;  | [optional] 
**expiration_month** | **int** | One or two digits expiration month (1-12).           | [optional] 
**expiration_year** | **int** | Four-digit expiration year.  | [optional] 
**security_code** | **str** | The CVV or CVV2 security code for the credit card or debit card.             Only required if changing expirationMonth, expirationYear, or cardHolderName.             To ensure PCI compliance, this value isn&#39;&#39;t stored and can&#39;&#39;t be queried.                    | [optional] 
**baid** | **str** | ID of a PayPal billing agreement. For example, I-1TJ3GAGG82Y9.  | [optional] 
**email** | **str** | Email address associated with the PayPal payment method.   | [optional] 
**preapproval_key** | **str** | The PayPal preapproval key.  | [optional] 
**google_bin** | **str** | This field is only available for Google Pay payment methods.  | [optional] 
**google_card_number** | **str** | This field is only available for Google Pay payment methods.  | [optional] 
**google_card_type** | **str** | This field is only available for Google Pay payment methods.   For Google Pay payment methods on Adyen, the first 100 characters of [paymentMethodVariant](https://docs.adyen.com/development-resources/paymentmethodvariant) returned from Adyen are stored in this field. | [optional] 
**google_expiry_date** | **str** | This field is only available for Google Pay payment methods.  | [optional] 
**google_gateway_token** | **str** | This field is only available for Google Pay payment methods.  | [optional] 
**apple_bin** | **str** | This field is only available for Apple Pay payment methods.  | [optional] 
**apple_card_number** | **str** | This field is only available for Apple Pay payment methods.  | [optional] 
**apple_card_type** | **str** | This field is only available for Apple Pay payment methods.   For Apple Pay payment methods on Adyen, the first 100 characters of [paymentMethodVariant](https://docs.adyen.com/development-resources/paymentmethodvariant) returned from Adyen are stored in this field. | [optional] 
**apple_expiry_date** | **str** | This field is only available for Apple Pay payment methods.  | [optional] 
**apple_gateway_token** | **str** | This field is only available for Apple Pay payment methods.  | [optional] 
**account_holder_info** | [**GetPMAccountHolderInfo**](GetPMAccountHolderInfo.md) |  | [optional] 
**bank_identification_number** | **str** | The first six or eight digits of the payment method&#39;s number, such as the credit card number or account number. Banks use this number to identify a payment method.  | [optional] 
**card_bin_info** | [**PaymentMethodResponseCardBinInfo**](PaymentMethodResponseCardBinInfo.md) |  | [optional] 
**created_by** | **str** | ID of the user who created this payment method. | [optional] 
**created_on** | **datetime** | The date and time when the payment method was created, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format.  | [optional] 
**credit_card_mask_number** | **str** | The masked credit card number, such as: &#x60;&#x60;&#x60; *********1112 &#x60;&#x60;&#x60;  | [optional] 
**credit_card_type** | **str** | The type of the credit card or debit card.  Possible values include &#x60;Visa&#x60;, &#x60;MasterCard&#x60;, &#x60;AmericanExpress&#x60;, &#x60;Discover&#x60;, &#x60;JCB&#x60;, and &#x60;Diners&#x60;. For more information about credit card types supported by different payment gateways, see [Supported Payment Gateways](https://knowledgecenter.zuora.com/CB_Billing/M_Payment_Gateways/Supported_Payment_Gateways).  **Note:** This field is only returned for the Credit Card and Debit Card payment types.  | [optional] 
**device_session_id** | **str** | The session ID of the user when the &#x60;PaymentMethod&#x60; was created or updated.  | [optional] 
**existing_mandate** | [**PaymentMethodMandateInfoMandateStatus**](PaymentMethodMandateInfoMandateStatus.md) |  | [optional] 
**id** | **str** | The payment method ID.  | [optional] 
**ip_address** | **str** | The IP address of the user when the payment method was created or updated.  | [optional] 
**is_default** | **bool** | Indicates whether this payment method is the default payment method for the account.  | [optional] 
**last_failed_sale_transaction_date** | **datetime** | The date of the last failed attempt to collect payment with this payment method.  | [optional] 
**last_transaction** | **str** | ID of the last transaction of this payment method. | [optional] 
**last_transaction_time** | **datetime** | The time when the last transaction of this payment method happened. | [optional] 
**mandate_info** | [**PaymentMethodResponseMandateInfo**](PaymentMethodResponseMandateInfo.md) |  | [optional] 
**max_consecutive_payment_failures** | **int** | The number of allowable consecutive failures Zuora attempts with the payment method before stopping.  | [optional] 
**num_consecutive_failures** | **int** | The number of consecutive failed payments for this payment method. It is reset to &#x60;0&#x60; upon successful payment.   | [optional] 
**payment_retry_window** | **int** | The retry interval setting, which prevents making a payment attempt if the last failed attempt was within the last specified number of hours.  | [optional] 
**second_token_id** | **str** | A gateway unique identifier that replaces sensitive payment method data.  **Note:** This field is only returned for the Credit Card Reference Transaction payment type.  | [optional] 
**status** | **str** | The status of the payment method.  | [optional] 
**token_id** | **str** | A gateway unique identifier that replaces sensitive payment method data or represents a gateway&#39;s unique customer profile.  **Note:** This field is only returned for the Credit Card Reference Transaction payment type.  | [optional] 
**total_number_of_error_payments** | **int** | The number of error payments that used this payment method.  | [optional] 
**total_number_of_processed_payments** | **int** | The number of successful payments that used this payment method.  | [optional] 
**type** | **str** | The type of the payment method. For example, &#x60;CreditCard&#x60;.  | [optional] 
**updated_by** | **str** | ID of the user who made the last update to this payment method. | [optional] 
**updated_on** | **datetime** | The last date and time when the payment method was updated, in &#x60;yyyy-mm-dd hh:mm:ss&#x60; format.  | [optional] 
**use_default_retry_rule** | **bool** | Indicates whether this payment method uses the default retry rules configured in the Zuora Payments settings.  | [optional] 

## Example

```python
from zuora_sdk.models.payment_method_response import PaymentMethodResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PaymentMethodResponse from a JSON string
payment_method_response_instance = PaymentMethodResponse.from_json(json)
# print the JSON string representation of the object
print(PaymentMethodResponse.to_json())

# convert the object into a dict
payment_method_response_dict = payment_method_response_instance.to_dict()
# create an instance of PaymentMethodResponse from a dict
payment_method_response_from_dict = PaymentMethodResponse.from_dict(payment_method_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


