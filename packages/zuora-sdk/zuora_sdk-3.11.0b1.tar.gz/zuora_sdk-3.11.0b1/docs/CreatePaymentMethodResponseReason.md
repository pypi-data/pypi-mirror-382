# CreatePaymentMethodResponseReason

Error information. Only applicable if the payment method was not created. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | **str** | Error code.  | [optional] 
**message** | **str** | Error message.  | [optional] 

## Example

```python
from zuora_sdk.models.create_payment_method_response_reason import CreatePaymentMethodResponseReason

# TODO update the JSON string below
json = "{}"
# create an instance of CreatePaymentMethodResponseReason from a JSON string
create_payment_method_response_reason_instance = CreatePaymentMethodResponseReason.from_json(json)
# print the JSON string representation of the object
print(CreatePaymentMethodResponseReason.to_json())

# convert the object into a dict
create_payment_method_response_reason_dict = create_payment_method_response_reason_instance.to_dict()
# create an instance of CreatePaymentMethodResponseReason from a dict
create_payment_method_response_reason_from_dict = CreatePaymentMethodResponseReason.from_dict(create_payment_method_response_reason_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


