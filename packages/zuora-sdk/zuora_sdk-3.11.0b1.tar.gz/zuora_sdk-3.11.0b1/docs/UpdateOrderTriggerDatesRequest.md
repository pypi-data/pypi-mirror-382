# UpdateOrderTriggerDatesRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**subscriptions** | [**List[UpdateOrderActionTriggerDatesRequest]**](UpdateOrderActionTriggerDatesRequest.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.update_order_trigger_dates_request import UpdateOrderTriggerDatesRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateOrderTriggerDatesRequest from a JSON string
update_order_trigger_dates_request_instance = UpdateOrderTriggerDatesRequest.from_json(json)
# print the JSON string representation of the object
print(UpdateOrderTriggerDatesRequest.to_json())

# convert the object into a dict
update_order_trigger_dates_request_dict = update_order_trigger_dates_request_instance.to_dict()
# create an instance of UpdateOrderTriggerDatesRequest from a dict
update_order_trigger_dates_request_from_dict = UpdateOrderTriggerDatesRequest.from_dict(update_order_trigger_dates_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


