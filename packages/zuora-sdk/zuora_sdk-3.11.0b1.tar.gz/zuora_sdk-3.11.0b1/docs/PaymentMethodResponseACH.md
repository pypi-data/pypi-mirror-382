# PaymentMethodResponseACH


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**bank_aba_code** | **str** | The nine-digit routing number or ABA number used by banks. This field is only required if the &#x60;type&#x60; field is set to &#x60;ACH&#x60;.  | [optional] 
**bank_account_name** | **str** | The name of the account holder, which can be either a person or a company. This field is only required if the &#x60;type&#x60; field is set to &#x60;ACH&#x60;.  | [optional] 
**bank_account_number** | **str** | The bank account number associated with the ACH payment. This field is only required if the &#x60;type&#x60; field is set to &#x60;ACH&#x60;. However, for creating tokenized ACH payment methods on Stripe v2, this field is optional if the &#x60;tokens&#x60; and &#x60;bankAccountMaskNumber&#x60; fields are specified.  | [optional] 
**bank_account_mask_number** | **str** | The masked bank account number associated with the ACH payment. This field is only required if the ACH payment method is created using tokens.  | [optional] 
**bank_account_type** | [**PaymentMethodACHBankAccountType**](PaymentMethodACHBankAccountType.md) |  | [optional] 
**bank_name** | **str** | The name of the bank where the ACH payment account is held. This field is only required if the &#x60;type&#x60; field is set to &#x60;ACH&#x60;.  When creating an ACH payment method on Adyen, this field is required by Zuora but it is not required by Adyen. To create the ACH payment method successfully, specify a real value for this field if you can. If it is not possible to get the real value for it, specify a dummy value.  | [optional] 

## Example

```python
from zuora_sdk.models.payment_method_response_ach import PaymentMethodResponseACH

# TODO update the JSON string below
json = "{}"
# create an instance of PaymentMethodResponseACH from a JSON string
payment_method_response_ach_instance = PaymentMethodResponseACH.from_json(json)
# print the JSON string representation of the object
print(PaymentMethodResponseACH.to_json())

# convert the object into a dict
payment_method_response_ach_dict = payment_method_response_ach_instance.to_dict()
# create an instance of PaymentMethodResponseACH from a dict
payment_method_response_ach_from_dict = PaymentMethodResponseACH.from_dict(payment_method_response_ach_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


