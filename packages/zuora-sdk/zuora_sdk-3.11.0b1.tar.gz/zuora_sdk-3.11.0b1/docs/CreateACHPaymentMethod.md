# CreateACHPaymentMethod


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
**mandate_info** | [**PaymentMethodRequestMandateInfo**](PaymentMethodRequestMandateInfo.md) |  | [optional] 
**mandate_id** | **str** | The mandate ID.   When creating an ACH payment method, if you need to pass in tokenized information, use the &#x60;mandateId&#x60; instead of &#x60;tokenId&#x60; field. | [optional] 
**mandate_received_status** | [**PaymentMethodMandateInfoMandateStatus**](PaymentMethodMandateInfoMandateStatus.md) |  | [optional] 
**existing_mandate_status** | [**PaymentMethodMandateInfoMandateStatus**](PaymentMethodMandateInfoMandateStatus.md) |  | [optional] 
**mandate_creation_date** | **date** | The date on which the mandate was created.  | [optional] 
**mandate_update_date** | **date** | The date on which the mandate was updated.  | [optional] 
**address_line1** | **str** | First address line, 255 characters or less.  | [optional] 
**address_line2** | **str** | Second address line, 255 characters or less.  | [optional] 
**email** | **str** | Card holder&#39;s email address, 80 characters or less.  | [optional] 
**bank_aba_code** | **str** | The nine-digit routing number or ABA number used by banks.  | 
**bank_account_name** | **str** | The name of the account holder, which can be either a person or a company.   For ACH payment methods on the BlueSnap integration, see [Overview of BlueSnap gateway integration](https://knowledgecenter.zuora.com/Zuora_Billing/Billing_and_Payments/M_Payment_Gateways/Supported_Payment_Gateways/BlueSnap_Gateway/Overview_of_BlueSnap_gateway_integration#Payer_Name_Extraction) for more information about how Zuora splits the string in this field into two parts and passes them to BlueSnap&#39;s &#x60;firstName&#x60; and &#x60;lastName&#x60; fields.  | 
**bank_account_number** | **str** | The bank account number associated with the ACH payment. This field is only required if the &#x60;type&#x60; field is set to &#x60;ACH&#x60;. However, for creating tokenized ACH payment methods on Stripe v2, this field is optional if the &#x60;tokens&#x60; and &#x60;bankAccountMaskNumber&#x60; fields are specified.  | [optional] 
**bank_account_mask_number** | **str** | The masked bank account number associated with the ACH payment. This field is only required if the ACH payment method is created using tokens.  | [optional] 
**bank_account_type** | [**PaymentMethodACHBankAccountType**](PaymentMethodACHBankAccountType.md) |  | 
**bank_name** | **str** | The name of the bank where the ACH payment account is held.   When creating an ACH payment method on Adyen, this field is required by Zuora but it is not required by Adyen. To create the ACH payment method successfully, specify a real value for this field if you can. If it is not possible to get the real value for it, specify a dummy value.  | 
**city** | **str** | City, 40 characters or less. It is recommended to provide the city and country information when creating a payment method. The information will be used to process payments. If the information is not provided during payment method creation, the city and country data will be missing during payment processing.  | [optional] 
**country** | **str** | Country, must be a valid country name or abbreviation.  See [Country Names and Their ISO Standard 2- and 3-Digit Codes](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/D_Country%2C_State%2C_and_Province_Codes/A_Country_Names_and_Their_ISO_Codes) for the list of supported country names and abbreviations.  It is recommended to provide the city and country information when creating a payment method. The information will be used to process payments. If the information is not provided during payment method creation, the city and country data will be missing during payment processing.  | [optional] 
**phone** | **str** | Phone number, 40 characters or less.  | [optional] 
**state** | **str** | State, must be a valid state name or 2-character abbreviation.  See [United States Standard State Codes](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/D_Country%2C_State%2C_and_Province_Codes/B_State_Names_and_2-Digit_Codes) and [Canadian Standard Province Codes](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/D_Country%2C_State%2C_and_Province_Codes/C_Canadian_Province_Names_and_2-Digit_Codes) for the list of supported names and abbreviations.  | [optional] 
**zip_code** | **str** | Zip code, 20 characters or less.  | [optional] 

## Example

```python
from zuora_sdk.models.create_ach_payment_method import CreateACHPaymentMethod

# TODO update the JSON string below
json = "{}"
# create an instance of CreateACHPaymentMethod from a JSON string
create_ach_payment_method_instance = CreateACHPaymentMethod.from_json(json)
# print the JSON string representation of the object
print(CreateACHPaymentMethod.to_json())

# convert the object into a dict
create_ach_payment_method_dict = create_ach_payment_method_instance.to_dict()
# create an instance of CreateACHPaymentMethod from a dict
create_ach_payment_method_from_dict = CreateACHPaymentMethod.from_dict(create_ach_payment_method_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


