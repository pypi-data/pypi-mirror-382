# SignUpPaymentMethod


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**second_token_id** | **str** | The second token id of CreditCardReferenceTransaction.  | [optional] 
**token_id** | **str** | The token id of payment method, required field of CreditCardReferenceTransaction type. | [optional] 
**baid** | **str** | ID of a PayPal billing agreement, for example, I-1TJ3GAGG82Y9.  | [optional] 
**email** | **str** | Email address associated with the payment method. This field is only supported for PayPal payment methods and is required if you want to create any of the following PayPal payment methods:   - PayPal Express Checkout payment method    - PayPal Adaptive payment method   - PayPal Commerce Platform payment method | [optional] 
**preapproval_key** | **str** | The PayPal preapproval key.  | [optional] 
**card_holder_info** | [**SignUpCreatePaymentMethodCardholderInfo**](SignUpCreatePaymentMethodCardholderInfo.md) |  | [optional] 
**card_number** | **str** | Credit card number.  | [optional] 
**card_type** | **str** | The type of the credit card.  Possible values include &#x60;Visa&#x60;, &#x60;MasterCard&#x60;, &#x60;AmericanExpress&#x60;, &#x60;Discover&#x60;, &#x60;JCB&#x60;, and &#x60;Diners&#x60;. For more information about credit card types supported by different payment gateways, see [Supported Payment Gateways](https://knowledgecenter.zuora.com/CB_Billing/M_Payment_Gateways/Supported_Payment_Gateways).  | [optional] 
**check_duplicated** | **bool** |  | [optional] 
**expiration_month** | **str** | One or two digit expiration month (1-12) of the credit card.  | [optional] 
**expiration_year** | **str** | Four-digit expiration year of the credit card.  | [optional] 
**mit_consent_agreement_ref** | **str** | Specifies your reference for the stored credential consent agreement that you have established with the customer. Only applicable if you set the &#x60;mitProfileAction&#x60; field.  | [optional] 
**mit_consent_agreement_src** | [**StoredCredentialProfileConsentAgreementSrc**](StoredCredentialProfileConsentAgreementSrc.md) |  | [optional] 
**mit_network_transaction_id** | **str** | Specifies the ID of a network transaction. Only applicable if you set the &#x60;mitProfileAction&#x60; field to &#x60;Persist&#x60;.  | [optional] 
**mit_profile_action** | [**StoredCredentialProfileAction**](StoredCredentialProfileAction.md) |  | [optional] 
**mit_profile_agreed_on** | **date** | The date on which the profile is agreed. The date format is &#x60;yyyy-mm-dd&#x60;.  | [optional] 
**mit_profile_type** | [**SignUpCreatePaymentMethodCreditCardMitProfileType**](SignUpCreatePaymentMethodCreditCardMitProfileType.md) |  | [optional] 
**security_code** | **str** | CVV or CVV2 security code of the credit card.  To ensure PCI compliance, this value is not stored and cannot be queried.  | [optional] 
**account_key** | **str** | Internal ID of the customer account that will own the payment method.  | [optional] 
**auth_gateway** | **str** | Internal ID of the payment gateway that Zuora will use to authorize the payments that are made with the payment method.   If you do not set this field, Zuora will use one of the following payment gateways instead:   * The default payment gateway of the customer account that owns the payment method, if the &#x60;accountKey&#x60; field is set.  * The default payment gateway of your Zuora tenant, if the &#x60;accountKey&#x60; field is not set. | [optional] 
**ip_address** | **str** | The IPv4 or IPv6 information of the user when the payment method is created or updated. Some gateways use this field for fraud prevention. If this field is passed to Zuora, Zuora directly passes it to gateways.    If the IP address length is beyond 45 characters, a validation error occurs. | [optional] 
**make_default** | **bool** | Specifies whether the payment method will be the default payment method of the customer account that owns the payment method. Only applicable if the &#x60;accountKey&#x60; field is set. | [optional] [default to False]
**type** | **str** | Type of payment method. The following types of the payment method are supported: | 

## Example

```python
from zuora_sdk.models.sign_up_payment_method import SignUpPaymentMethod

# TODO update the JSON string below
json = "{}"
# create an instance of SignUpPaymentMethod from a JSON string
sign_up_payment_method_instance = SignUpPaymentMethod.from_json(json)
# print the JSON string representation of the object
print(SignUpPaymentMethod.to_json())

# convert the object into a dict
sign_up_payment_method_dict = sign_up_payment_method_instance.to_dict()
# create an instance of SignUpPaymentMethod from a dict
sign_up_payment_method_from_dict = SignUpPaymentMethod.from_dict(sign_up_payment_method_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


