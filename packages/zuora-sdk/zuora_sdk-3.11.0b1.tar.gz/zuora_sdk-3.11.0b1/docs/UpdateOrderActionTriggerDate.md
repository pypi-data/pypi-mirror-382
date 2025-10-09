# UpdateOrderActionTriggerDate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | [**OrderActionTriggerDatesName**](OrderActionTriggerDatesName.md) |  | [optional] 
**trigger_date** | **date** | Trigger date in YYYY-MM-DD format. The date you are to set as the service activation date or the customer acceptance date.  | [optional] 

## Example

```python
from zuora_sdk.models.update_order_action_trigger_date import UpdateOrderActionTriggerDate

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateOrderActionTriggerDate from a JSON string
update_order_action_trigger_date_instance = UpdateOrderActionTriggerDate.from_json(json)
# print the JSON string representation of the object
print(UpdateOrderActionTriggerDate.to_json())

# convert the object into a dict
update_order_action_trigger_date_dict = update_order_action_trigger_date_instance.to_dict()
# create an instance of UpdateOrderActionTriggerDate from a dict
update_order_action_trigger_date_from_dict = UpdateOrderActionTriggerDate.from_dict(update_order_action_trigger_date_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


