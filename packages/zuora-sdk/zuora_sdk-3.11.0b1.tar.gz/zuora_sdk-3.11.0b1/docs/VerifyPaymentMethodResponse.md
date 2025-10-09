# VerifyPaymentMethodResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**payment_method_id** | **str** | The ID of the verified payment method.  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 

## Example

```python
from zuora_sdk.models.verify_payment_method_response import VerifyPaymentMethodResponse

# TODO update the JSON string below
json = "{}"
# create an instance of VerifyPaymentMethodResponse from a JSON string
verify_payment_method_response_instance = VerifyPaymentMethodResponse.from_json(json)
# print the JSON string representation of the object
print(VerifyPaymentMethodResponse.to_json())

# convert the object into a dict
verify_payment_method_response_dict = verify_payment_method_response_instance.to_dict()
# create an instance of VerifyPaymentMethodResponse from a dict
verify_payment_method_response_from_dict = VerifyPaymentMethodResponse.from_dict(verify_payment_method_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


