# CreatePaymentMethodDecryptionResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **str** | The payment amount contained within the encrypted token.  | [optional] 
**payment_id** | **str** | The ID of newly processed payment,  | [optional] 
**payment_method_id** | **str** | ID of the newly-created payment method.  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 

## Example

```python
from zuora_sdk.models.create_payment_method_decryption_response import CreatePaymentMethodDecryptionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreatePaymentMethodDecryptionResponse from a JSON string
create_payment_method_decryption_response_instance = CreatePaymentMethodDecryptionResponse.from_json(json)
# print the JSON string representation of the object
print(CreatePaymentMethodDecryptionResponse.to_json())

# convert the object into a dict
create_payment_method_decryption_response_dict = create_payment_method_decryption_response_instance.to_dict()
# create an instance of CreatePaymentMethodDecryptionResponse from a dict
create_payment_method_decryption_response_from_dict = CreatePaymentMethodDecryptionResponse.from_dict(create_payment_method_decryption_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


