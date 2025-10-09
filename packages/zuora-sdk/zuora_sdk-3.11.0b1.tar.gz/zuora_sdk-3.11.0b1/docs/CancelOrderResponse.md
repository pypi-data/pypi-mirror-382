# CancelOrderResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**account_number** | **str** | The account number for the order. | [optional] 
**cancel_reason** | **str** | The reason for cancelling the order. | [optional] 
**order_number** | **str** | The order number of the order created. | [optional] 
**status** | **str** | Status of the order. &#x60;Cancelled&#x60; is only valid value. | [optional] 

## Example

```python
from zuora_sdk.models.cancel_order_response import CancelOrderResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CancelOrderResponse from a JSON string
cancel_order_response_instance = CancelOrderResponse.from_json(json)
# print the JSON string representation of the object
print(CancelOrderResponse.to_json())

# convert the object into a dict
cancel_order_response_dict = cancel_order_response_instance.to_dict()
# create an instance of CancelOrderResponse from a dict
cancel_order_response_from_dict = CancelOrderResponse.from_dict(cancel_order_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


