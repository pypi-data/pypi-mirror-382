# GetPaymentMethodResponseACHForAccount


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**bank_aba_code** | **str** | The nine-digit routing number or ABA number used by banks. This field is only required if the &#x60;type&#x60; field is set to &#x60;ACH&#x60;. | [optional] 
**bank_account_name** | **str** | The name of the account holder, which can be either a person or a company. This field is only required if the &#x60;type&#x60; field is set to &#x60;ACH&#x60;. | [optional] 

## Example

```python
from zuora_sdk.models.get_payment_method_response_ach_for_account import GetPaymentMethodResponseACHForAccount

# TODO update the JSON string below
json = "{}"
# create an instance of GetPaymentMethodResponseACHForAccount from a JSON string
get_payment_method_response_ach_for_account_instance = GetPaymentMethodResponseACHForAccount.from_json(json)
# print the JSON string representation of the object
print(GetPaymentMethodResponseACHForAccount.to_json())

# convert the object into a dict
get_payment_method_response_ach_for_account_dict = get_payment_method_response_ach_for_account_instance.to_dict()
# create an instance of GetPaymentMethodResponseACHForAccount from a dict
get_payment_method_response_ach_for_account_from_dict = GetPaymentMethodResponseACHForAccount.from_dict(get_payment_method_response_ach_for_account_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


