# UpdateOrderAction


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**change_reason** | **str** | The change reason set for an order action when the order action is updated. | [optional] 
**custom_fields** | **Dict[str, object]** | Container for custom fields of an Order Action object.  | [optional] 

## Example

```python
from zuora_sdk.models.update_order_action import UpdateOrderAction

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateOrderAction from a JSON string
update_order_action_instance = UpdateOrderAction.from_json(json)
# print the JSON string representation of the object
print(UpdateOrderAction.to_json())

# convert the object into a dict
update_order_action_dict = update_order_action_instance.to_dict()
# create an instance of UpdateOrderAction from a dict
update_order_action_from_dict = UpdateOrderAction.from_dict(update_order_action_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


