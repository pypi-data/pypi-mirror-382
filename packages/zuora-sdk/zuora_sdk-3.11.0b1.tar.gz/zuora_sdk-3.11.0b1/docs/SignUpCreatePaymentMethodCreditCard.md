# SignUpCreatePaymentMethodCreditCard


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
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

## Example

```python
from zuora_sdk.models.sign_up_create_payment_method_credit_card import SignUpCreatePaymentMethodCreditCard

# TODO update the JSON string below
json = "{}"
# create an instance of SignUpCreatePaymentMethodCreditCard from a JSON string
sign_up_create_payment_method_credit_card_instance = SignUpCreatePaymentMethodCreditCard.from_json(json)
# print the JSON string representation of the object
print(SignUpCreatePaymentMethodCreditCard.to_json())

# convert the object into a dict
sign_up_create_payment_method_credit_card_dict = sign_up_create_payment_method_credit_card_instance.to_dict()
# create an instance of SignUpCreatePaymentMethodCreditCard from a dict
sign_up_create_payment_method_credit_card_from_dict = SignUpCreatePaymentMethodCreditCard.from_dict(sign_up_create_payment_method_credit_card_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


