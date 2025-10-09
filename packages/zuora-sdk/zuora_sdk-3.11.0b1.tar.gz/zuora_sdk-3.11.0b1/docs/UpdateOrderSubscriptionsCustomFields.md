# UpdateOrderSubscriptionsCustomFields


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**order_actions** | [**List[UpdateOrderSubscriptionsOrderActionsCustomFields]**](UpdateOrderSubscriptionsOrderActionsCustomFields.md) |  | [optional] 
**subscription_number** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.update_order_subscriptions_custom_fields import UpdateOrderSubscriptionsCustomFields

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateOrderSubscriptionsCustomFields from a JSON string
update_order_subscriptions_custom_fields_instance = UpdateOrderSubscriptionsCustomFields.from_json(json)
# print the JSON string representation of the object
print(UpdateOrderSubscriptionsCustomFields.to_json())

# convert the object into a dict
update_order_subscriptions_custom_fields_dict = update_order_subscriptions_custom_fields_instance.to_dict()
# create an instance of UpdateOrderSubscriptionsCustomFields from a dict
update_order_subscriptions_custom_fields_from_dict = UpdateOrderSubscriptionsCustomFields.from_dict(update_order_subscriptions_custom_fields_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


