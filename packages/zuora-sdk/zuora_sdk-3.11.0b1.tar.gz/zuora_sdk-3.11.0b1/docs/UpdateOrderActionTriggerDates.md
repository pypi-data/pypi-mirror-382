# UpdateOrderActionTriggerDates


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**charges** | [**List[UpdateOrderActionChargeTriggerDate]**](UpdateOrderActionChargeTriggerDate.md) |  | [optional] 
**sequence** | **int** | Identifies which order action will have its triggering dates updated.   | 
**trigger_dates** | [**List[UpdateOrderActionTriggerDate]**](UpdateOrderActionTriggerDate.md) | Container for the service activation and customer acceptance dates of the order action. | [optional] 

## Example

```python
from zuora_sdk.models.update_order_action_trigger_dates import UpdateOrderActionTriggerDates

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateOrderActionTriggerDates from a JSON string
update_order_action_trigger_dates_instance = UpdateOrderActionTriggerDates.from_json(json)
# print the JSON string representation of the object
print(UpdateOrderActionTriggerDates.to_json())

# convert the object into a dict
update_order_action_trigger_dates_dict = update_order_action_trigger_dates_instance.to_dict()
# create an instance of UpdateOrderActionTriggerDates from a dict
update_order_action_trigger_dates_from_dict = UpdateOrderActionTriggerDates.from_dict(update_order_action_trigger_dates_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


