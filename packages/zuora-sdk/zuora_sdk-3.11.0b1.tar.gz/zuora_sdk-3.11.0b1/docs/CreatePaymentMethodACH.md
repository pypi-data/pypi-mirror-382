# CreatePaymentMethodACH


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**address_line1** | **str** | First address line, 255 characters or less.  | [optional] 
**address_line2** | **str** | Second address line, 255 characters or less.  | [optional] 
**bank_aba_code** | **str** | The nine-digit routing number or ABA number used by banks. This field is only required if the &#x60;type&#x60; field is set to &#x60;ACH&#x60;.  | [optional] 
**bank_account_name** | **str** | The name of the account holder, which can be either a person or a company. This field is only required if the &#x60;type&#x60; field is set to &#x60;ACH&#x60;.  For ACH payment methods on the BlueSnap integration, see [Overview of BlueSnap gateway integration](https://knowledgecenter.zuora.com/Zuora_Billing/Billing_and_Payments/M_Payment_Gateways/Supported_Payment_Gateways/BlueSnap_Gateway/Overview_of_BlueSnap_gateway_integration#Payer_Name_Extraction) for more information about how Zuora splits the string in this field into two parts and passes them to BlueSnap&#39;s &#x60;firstName&#x60; and &#x60;lastName&#x60; fields.  | [optional] 
**bank_account_number** | **str** | The bank account number associated with the ACH payment. This field is only required if the &#x60;type&#x60; field is set to &#x60;ACH&#x60;. However, for creating tokenized ACH payment methods on Stripe v2, this field is optional if the &#x60;tokens&#x60; and &#x60;bankAccountMaskNumber&#x60; fields are specified.  | [optional] 
**bank_account_mask_number** | **str** | The masked bank account number associated with the ACH payment. This field is only required if the ACH payment method is created using tokens.  | [optional] 
**bank_account_type** | [**PaymentMethodACHBankAccountType**](PaymentMethodACHBankAccountType.md) |  | [optional] 
**bank_name** | **str** | The name of the bank where the ACH payment account is held. This field is only required if the &#x60;type&#x60; field is set to &#x60;ACH&#x60;.  When creating an ACH payment method on Adyen, this field is required by Zuora but it is not required by Adyen. To create the ACH payment method successfully, specify a real value for this field if you can. If it is not possible to get the real value for it, specify a dummy value.  | [optional] 
**city** | **str** | City, 40 characters or less. It is recommended to provide the city and country information when creating a payment method. The information will be used to process payments. If the information is not provided during payment method creation, the city and country data will be missing during payment processing.  | [optional] 
**country** | **str** | Country, must be a valid country name or abbreviation.  See [Country Names and Their ISO Standard 2- and 3-Digit Codes](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/D_Country%2C_State%2C_and_Province_Codes/A_Country_Names_and_Their_ISO_Codes) for the list of supported country names and abbreviations.  It is recommended to provide the city and country information when creating a payment method. The information will be used to process payments. If the information is not provided during payment method creation, the city and country data will be missing during payment processing.  | [optional] 
**phone** | **str** | Phone number, 40 characters or less.  | [optional] 
**state** | **str** | State, must be a valid state name or 2-character abbreviation.  See [United States Standard State Codes](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/D_Country%2C_State%2C_and_Province_Codes/B_State_Names_and_2-Digit_Codes) and [Canadian Standard Province Codes](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/D_Country%2C_State%2C_and_Province_Codes/C_Canadian_Province_Names_and_2-Digit_Codes) for the list of supported names and abbreviations.  | [optional] 
**zip_code** | **str** | Zip code, 20 characters or less.  | [optional] 

## Example

```python
from zuora_sdk.models.create_payment_method_ach import CreatePaymentMethodACH

# TODO update the JSON string below
json = "{}"
# create an instance of CreatePaymentMethodACH from a JSON string
create_payment_method_ach_instance = CreatePaymentMethodACH.from_json(json)
# print the JSON string representation of the object
print(CreatePaymentMethodACH.to_json())

# convert the object into a dict
create_payment_method_ach_dict = create_payment_method_ach_instance.to_dict()
# create an instance of CreatePaymentMethodACH from a dict
create_payment_method_ach_from_dict = CreatePaymentMethodACH.from_dict(create_payment_method_ach_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


