# UpdateOrderActionTriggerDatesRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**order_actions** | [**List[UpdateOrderActionTriggerDates]**](UpdateOrderActionTriggerDates.md) |  | [optional] 
**subscription_number** | **str** | Subscription number of a subscription in the &#x60;Pending&#x60; order for which you are to update the triggering dates. For example, A-S00000001. | 

## Example

```python
from zuora_sdk.models.update_order_action_trigger_dates_request import UpdateOrderActionTriggerDatesRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateOrderActionTriggerDatesRequest from a JSON string
update_order_action_trigger_dates_request_instance = UpdateOrderActionTriggerDatesRequest.from_json(json)
# print the JSON string representation of the object
print(UpdateOrderActionTriggerDatesRequest.to_json())

# convert the object into a dict
update_order_action_trigger_dates_request_dict = update_order_action_trigger_dates_request_instance.to_dict()
# create an instance of UpdateOrderActionTriggerDatesRequest from a dict
update_order_action_trigger_dates_request_from_dict = UpdateOrderActionTriggerDatesRequest.from_dict(update_order_action_trigger_dates_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


