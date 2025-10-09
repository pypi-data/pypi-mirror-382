# CreateCreditCardPaymentMethod


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_key** | **str** | Internal ID of the customer account that will own the payment method. To create an orphan payment method that is not associated with any customer account, you do not need to specify this field during creation. However, you must associate the orphan payment method with a customer account within 10 days. Otherwise, this orphan payment method will be deleted.  | [optional] 
**payment_method_number** | **str** | To avoid the repetitive creation of identical payment methods, you can associate a unique identifier with the payment method.  You can specify a string within the allowed limits, or if none is provided, the system will automatically generate one for the payment method.  | [optional] 
**payment_gateway_number** | **str** | The natural key for the payment gateway. | [optional] 
**screening_amount** | **float** | For [Chase Paymentech Orbital Gateway](https://knowledgecenter.zuora.com/Zuora_Payments/Payment_gateway_integrations/Supported_payment_gateways/Chase_Orbital_Payment_Gateway) integrations,  if the Safetech Fraud service is enabled, use this field to pass in the amount used for fraud screening for Credit Card validation transactions.  Two-decimal amount is supported.  If the &#x60;screeningAmount&#x60; field is not specified, the authorization amount is used for fraud screening.  | [optional] 
**auth_gateway** | **str** | Internal ID of the payment gateway that Zuora will use to authorize the payments that are made with the payment method.  If you do not set this field, Zuora will use one of the following payment gateways instead:  * The default payment gateway of the customer account that owns the payment method, if the &#x60;accountKey&#x60; field is set. * The default payment gateway of your Zuora tenant, if the &#x60;accountKey&#x60; field is not set.  | [optional] 
**gateway_options** | [**GatewayOptions**](GatewayOptions.md) |  | [optional] 
**ip_address** | **str** | The IPv4 or IPv6 information of the user when the payment method is created or updated. Some gateways use this field for fraud prevention. If this field is passed to Zuora, Zuora directly passes it to gateways. If the IP address length is beyond 45 characters, a validation error occurs. For validating SEPA payment methods on Stripe v2, this field is required.  | [optional] 
**make_default** | **bool** | Specifies whether the payment method will be the default payment method of the customer account that owns the payment method. Only applicable if the &#x60;accountKey&#x60; field is set.  When you set this field to &#x60;true&#x60;, make sure the payment method is supported by the default payment gateway.  | [optional] [default to False]
**processing_options** | [**PaymentMethodRequestProcessingOptions**](PaymentMethodRequestProcessingOptions.md) |  | [optional] 
**skip_validation** | **bool** | Specify whether to skip the validation of the information through the payment gateway. For example, when migrating your payment methods, you can set this field to &#x60;true&#x60; to skip the validation.  | [optional] [default to False]
**type** | **str** | Type of the payment method. Possible values include:    * &#x60;CreditCard&#x60; - Credit card payment method.   * &#x60;CreditCardReferenceTransaction&#x60; - Credit Card Reference Transaction. See [Supported payment methods](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/L_Payment_Methods/Supported_Payment_Methods) for payment gateways that support this type of payment method.   * &#x60;ACH&#x60; - ACH payment method.   * &#x60;SEPA&#x60; - Single Euro Payments Area.   * &#x60;Betalingsservice&#x60; - Direct Debit DK.   * &#x60;Autogiro&#x60; - Direct Debit SE.   * &#x60;Bacs&#x60; - Direct Debit UK.   * &#x60;Becs&#x60; - Direct Entry AU.   * &#x60;Becsnz&#x60; - Direct Debit NZ.   * &#x60;PAD&#x60; - Pre-Authorized Debit.   * &#x60;PayPalCP&#x60; - PayPal Commerce Platform payment method. Use this type if you are using a [PayPal Commerce Platform Gateway](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/M_Payment_Gateways/Supported_Payment_Gateways/PayPal_Commerce_Platform_Gateway) instance.   * &#x60;PayPalEC&#x60; - PayPal Express Checkout payment method. Use this type if you are using a [PayPal Payflow Pro Gateway](https://knowledgecenter.zuora.com/CB_Billing/M_Payment_Gateways/Supported_Payment_Gateways/PayPal_Payflow_Pro%2C_Website_Payments_Payflow_Edition%2C_Website_Pro_Payment_Gateway) instance.   * &#x60;PayPalNativeEC&#x60; - PayPal Native Express Checkout payment method. Use this type if you are using a [PayPal Express Checkout Gateway](https://knowledgecenter.zuora.com/CB_Billing/M_Payment_Gateways/Supported_Payment_Gateways/PayPal_Express_Checkout_Gateway) instance.   * &#x60;PayPalAdaptive&#x60; - PayPal Adaptive payment method. Use this type if you are using a [PayPal Adaptive Payment Gateway](https://knowledgecenter.zuora.com/CB_Billing/M_Payment_Gateways/Supported_Payment_Gateways/PayPal_Adaptive_Payments_Gateway) instance.   * &#x60;AdyenApplePay&#x60; - Apple Pay on Adyen Integration v2.0. See [Set up Adyen Apple Pay](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/L_Payment_Methods/Payment_Method_Types/Apple_Pay_on_Web/Set_up_Adyen_Apple_Pay) for details.   * &#x60;AdyenGooglePay&#x60; - Google Pay on Adyen Integration v2.0. See [Set up Adyen Google Pay](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/L_Payment_Methods/Payment_Method_Types/Set_up_Adyen_Google_Pay) for details.   * &#x60;GooglePay&#x60; - Google Pay on Chase Paymentech Orbital gateway integration. See [Set up Google Pay on Chase](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/L_Payment_Methods/Payment_Method_Types/Set_up_Google_Pay_on_Chase) for details.   * You can also specify a custom payment method type. See [Set up custom payment gateways and payment methods](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/MB_Set_up_custom_payment_gateways_and_payment_methods) for details.    Note that Zuora is continuously adding new payment method types.  | 
**currency_code** | **str** | The currency code of the payment method. | [optional] 
**tokenize** | **bool** | Specifies whether to tokenize the payment method. | [optional] [default to False]
**tokens** | [**PaymentMethodRequestTokens**](PaymentMethodRequestTokens.md) |  | [optional] 
**card_holder_info** | [**CreatePaymentMethodCardholderInfo**](CreatePaymentMethodCardholderInfo.md) |  | [optional] 
**card_number** | **str** | Credit card number. This field is required if &#x60;type&#x60; is set to &#x60;CreditCard&#x60;. However, for creating tokenized credit card payment methods, this field is optional if the &#x60;tokens&#x60; and &#x60;cardMaskNumber&#x60; fields are specified.  | [optional] 
**card_mask_number** | **str** | The masked card number associated with the credit card payment. This field is only required if the credit card payment method is created using tokens.  | [optional] 
**card_type** | **str** | The type of the credit card. This field is required if &#x60;type&#x60; is set to &#x60;CreditCard&#x60;.  Possible values include &#x60;Visa&#x60;, &#x60;MasterCard&#x60;, &#x60;AmericanExpress&#x60;, &#x60;Discover&#x60;, &#x60;JCB&#x60;, and &#x60;Diners&#x60;. For more information about credit card types supported by different payment gateways, see [Supported Payment Gateways](https://knowledgecenter.zuora.com/CB_Billing/M_Payment_Gateways/Supported_Payment_Gateways).  | 
**identity_number** | **str** | The identity number of the customer. | [optional] 
**mandate_info** | [**PaymentMethodRequestMandateInfo**](PaymentMethodRequestMandateInfo.md) |  | [optional] 
**check_duplicated** | **bool** | Indicates whether the duplication check is performed when you create a new credit card payment method. The default value is &#x60;false&#x60;. With this field set to &#x60;true&#x60;, Zuora will check all active payment methods associated with the same billing account to ensure that no duplicate credit card payment methods are created. An error is returned if a duplicate payment method is found. The following fields are used for the duplication check: - &#x60;cardHolderName&#x60; - &#x60;expirationMonth&#x60; - &#x60;expirationYear&#x60; - &#x60;creditCardMaskNumber&#x60;. It is the masked credit card number generated by Zuora. For example: &#x60;&#x60;&#x60; ************1234 &#x60;&#x60;&#x60;  | [optional] 
**expiration_month** | **int** | One or two digit expiration month (1-12) of the credit card. This field is required if &#x60;type&#x60; is set to &#x60;CreditCard&#x60;. However, for creating tokenized credit card payment methods, this field is optional if the &#x60;tokens&#x60; and &#x60;cardMaskNumber&#x60; fields are specified.  | [optional] 
**expiration_year** | **int** | Four-digit expiration year of the credit card. This field is required if &#x60;type&#x60; is set to &#x60;CreditCard&#x60;. However, for creating tokenized credit card payment methods, this field is optional if the &#x60;tokens&#x60; and &#x60;cardMaskNumber&#x60; fields are specified.  | [optional] 
**mit_consent_agreement_ref** | **str** | Specifies your reference for the stored credential consent agreement that you have established with the customer. Only applicable if you set the &#x60;mitProfileAction&#x60; field.  | [optional] 
**mit_consent_agreement_src** | [**StoredCredentialProfileConsentAgreementSrc**](StoredCredentialProfileConsentAgreementSrc.md) |  | [optional] 
**mit_network_transaction_id** | **str** | Specifies the ID of a network transaction. Only applicable if you set the &#x60;mitProfileAction&#x60; field to &#x60;Persist&#x60;.  | [optional] 
**mit_profile_action** | [**StoredCredentialProfileAction**](StoredCredentialProfileAction.md) |  | [optional] 
**mit_profile_agreed_on** | **date** | The date on which the profile is agreed. The date format is &#x60;yyyy-mm-dd&#x60;.  | [optional] 
**mit_profile_type** | [**StoredCredentialProfileType**](StoredCredentialProfileType.md) |  | [optional] 
**security_code** | **str** | CVV or CVV2 security code of the credit card.  To ensure PCI compliance, this value is not stored and cannot be queried.  | [optional] 
**cryptogram** | **str** | Cryptogram value supplied by the token provider if DPAN or network scheme token is present  To ensure PCI compliance, this value is not stored and cannot be queried.  | [optional] 

## Example

```python
from zuora_sdk.models.create_credit_card_payment_method import CreateCreditCardPaymentMethod

# TODO update the JSON string below
json = "{}"
# create an instance of CreateCreditCardPaymentMethod from a JSON string
create_credit_card_payment_method_instance = CreateCreditCardPaymentMethod.from_json(json)
# print the JSON string representation of the object
print(CreateCreditCardPaymentMethod.to_json())

# convert the object into a dict
create_credit_card_payment_method_dict = create_credit_card_payment_method_instance.to_dict()
# create an instance of CreateCreditCardPaymentMethod from a dict
create_credit_card_payment_method_from_dict = CreateCreditCardPaymentMethod.from_dict(create_credit_card_payment_method_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


