# GetAccountPaymentMethodResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**default_payment_method_id** | **str** | ID of the default payment method for the account.  | [optional] 
**payment_gateway** | **str** | The name of the payment gateway instance. If null or left unassigned, the Account will use the Default Gateway. | [optional] 
**returned_payment_method_type** | [**List[GetPaymentMethodForAccountResponse]**](GetPaymentMethodForAccountResponse.md) | Container for a specific type of payment method on the customer account. For example, &#x60;creditcard&#x60;, &#x60;debitcard&#x60;, &#x60;creditcardreferencetransaction&#x60;, &#x60;ach&#x60;, etc. Each &#x60;returnedPaymentMethodType&#x60; array contains one or more payment methods of that payment method type.   **Note:** The response could return more than one payment method type arrays. See **Response samples** as an example. | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 

## Example

```python
from zuora_sdk.models.get_account_payment_method_response import GetAccountPaymentMethodResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetAccountPaymentMethodResponse from a JSON string
get_account_payment_method_response_instance = GetAccountPaymentMethodResponse.from_json(json)
# print the JSON string representation of the object
print(GetAccountPaymentMethodResponse.to_json())

# convert the object into a dict
get_account_payment_method_response_dict = get_account_payment_method_response_instance.to_dict()
# create an instance of GetAccountPaymentMethodResponse from a dict
get_account_payment_method_response_from_dict = GetAccountPaymentMethodResponse.from_dict(get_account_payment_method_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


