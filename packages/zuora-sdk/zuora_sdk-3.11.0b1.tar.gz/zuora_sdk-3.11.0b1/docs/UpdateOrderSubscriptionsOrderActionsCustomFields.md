# UpdateOrderSubscriptionsOrderActionsCustomFields


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_fields** | **Dict[str, object]** | Container for custom fields of an Order Action object.  | [optional] 
**order_action_id** | **str** | The Id of the order action in the order. You can provide either the &#x60;sequence&#x60; or the &#x60;orderActionId&#x60; field to specify which order action to update. You cannot use then both at the same time. | [optional] 
**sequence** | **int** | The sequence number of the order action in the order. You can provide either the &#x60;sequence&#x60; or the &#x60;orderActionId&#x60; field to specify which order action to update. You cannot use then both at the same time. | [optional] 

## Example

```python
from zuora_sdk.models.update_order_subscriptions_order_actions_custom_fields import UpdateOrderSubscriptionsOrderActionsCustomFields

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateOrderSubscriptionsOrderActionsCustomFields from a JSON string
update_order_subscriptions_order_actions_custom_fields_instance = UpdateOrderSubscriptionsOrderActionsCustomFields.from_json(json)
# print the JSON string representation of the object
print(UpdateOrderSubscriptionsOrderActionsCustomFields.to_json())

# convert the object into a dict
update_order_subscriptions_order_actions_custom_fields_dict = update_order_subscriptions_order_actions_custom_fields_instance.to_dict()
# create an instance of UpdateOrderSubscriptionsOrderActionsCustomFields from a dict
update_order_subscriptions_order_actions_custom_fields_from_dict = UpdateOrderSubscriptionsOrderActionsCustomFields.from_dict(update_order_subscriptions_order_actions_custom_fields_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


