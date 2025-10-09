# CreatePaymentMethodResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[CreatePaymentMethodResponseReason]**](CreatePaymentMethodResponseReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**id** | **str** | Internal ID of the payment method that was created.  | [optional] 

## Example

```python
from zuora_sdk.models.create_payment_method_response import CreatePaymentMethodResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreatePaymentMethodResponse from a JSON string
create_payment_method_response_instance = CreatePaymentMethodResponse.from_json(json)
# print the JSON string representation of the object
print(CreatePaymentMethodResponse.to_json())

# convert the object into a dict
create_payment_method_response_dict = create_payment_method_response_instance.to_dict()
# create an instance of CreatePaymentMethodResponse from a dict
create_payment_method_response_from_dict = CreatePaymentMethodResponse.from_dict(create_payment_method_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


