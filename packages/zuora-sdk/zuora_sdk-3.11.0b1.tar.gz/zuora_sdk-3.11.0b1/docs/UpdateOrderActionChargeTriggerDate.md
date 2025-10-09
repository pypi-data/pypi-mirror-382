# UpdateOrderActionChargeTriggerDate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**charge_number** | **str** | Charge number of the charge which needs the triggering date to be provided. The charge&#39;s &#x60;triggerEvent&#x60; must have been set as &#x60;SpecificDate&#x60;. | [optional] 
**specific_trigger_date** | **date** | Date in YYYY-MM-DD format. The specific trigger date you are to set for the charge. | [optional] 
**estimated_start_date** | **date** | Date in YYYY-MM-DD format. The estimated start date of the pending charge. This is the date when the charge is expected to start. | [optional] 

## Example

```python
from zuora_sdk.models.update_order_action_charge_trigger_date import UpdateOrderActionChargeTriggerDate

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateOrderActionChargeTriggerDate from a JSON string
update_order_action_charge_trigger_date_instance = UpdateOrderActionChargeTriggerDate.from_json(json)
# print the JSON string representation of the object
print(UpdateOrderActionChargeTriggerDate.to_json())

# convert the object into a dict
update_order_action_charge_trigger_date_dict = update_order_action_charge_trigger_date_instance.to_dict()
# create an instance of UpdateOrderActionChargeTriggerDate from a dict
update_order_action_charge_trigger_date_from_dict = UpdateOrderActionChargeTriggerDate.from_dict(update_order_action_charge_trigger_date_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


