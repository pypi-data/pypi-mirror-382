# PaymentMethodRequestTokens

The tokens for the payment method.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**gateway_type** | **str** | the gateway type | [optional] 
**token_id** | **str** | the token id | [optional] 
**second_token_id** | **str** | the second token id | [optional] 
**third_token_id** | **str** | the third token id | [optional] 

## Example

```python
from zuora_sdk.models.payment_method_request_tokens import PaymentMethodRequestTokens

# TODO update the JSON string below
json = "{}"
# create an instance of PaymentMethodRequestTokens from a JSON string
payment_method_request_tokens_instance = PaymentMethodRequestTokens.from_json(json)
# print the JSON string representation of the object
print(PaymentMethodRequestTokens.to_json())

# convert the object into a dict
payment_method_request_tokens_dict = payment_method_request_tokens_instance.to_dict()
# create an instance of PaymentMethodRequestTokens from a dict
payment_method_request_tokens_from_dict = PaymentMethodRequestTokens.from_dict(payment_method_request_tokens_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


