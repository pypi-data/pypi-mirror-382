# UpdatePaymentMethodResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**id** | **str** | Internal ID of the payment method that was created. | [optional] 

## Example

```python
from zuora_sdk.models.update_payment_method_response import UpdatePaymentMethodResponse

# TODO update the JSON string below
json = "{}"
# create an instance of UpdatePaymentMethodResponse from a JSON string
update_payment_method_response_instance = UpdatePaymentMethodResponse.from_json(json)
# print the JSON string representation of the object
print(UpdatePaymentMethodResponse.to_json())

# convert the object into a dict
update_payment_method_response_dict = update_payment_method_response_instance.to_dict()
# create an instance of UpdatePaymentMethodResponse from a dict
update_payment_method_response_from_dict = UpdatePaymentMethodResponse.from_dict(update_payment_method_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


