# UpdateOrderTriggerDatesResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**account_number** | **str** | The account number for the order. | [optional] 
**order_number** | **str** | The order number of the order updated. | [optional] 
**status** | **str** | Status of the order. | [optional] 
**subscriptions** | [**List[UpdateOrderTriggerDateResponse]**](UpdateOrderTriggerDateResponse.md) | The subscriptions updated. | [optional] 

## Example

```python
from zuora_sdk.models.update_order_trigger_dates_response import UpdateOrderTriggerDatesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateOrderTriggerDatesResponse from a JSON string
update_order_trigger_dates_response_instance = UpdateOrderTriggerDatesResponse.from_json(json)
# print the JSON string representation of the object
print(UpdateOrderTriggerDatesResponse.to_json())

# convert the object into a dict
update_order_trigger_dates_response_dict = update_order_trigger_dates_response_instance.to_dict()
# create an instance of UpdateOrderTriggerDatesResponse from a dict
update_order_trigger_dates_response_from_dict = UpdateOrderTriggerDatesResponse.from_dict(update_order_trigger_dates_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


