# OrderActionRatePlanOrderAction

Represents the processed order action.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**add_product** | [**OrderActionRatePlanOverride**](OrderActionRatePlanOverride.md) |  | [optional] 
**custom_fields** | **Dict[str, object]** | Container for custom fields of an Order Action object.  | [optional] 
**id** | **str** | The Id of the order action processed in the order. | [optional] 
**remove_product** | [**OrderActionRatePlanRemoveProduct**](OrderActionRatePlanRemoveProduct.md) |  | [optional] 
**type** | [**OrderActionRatePlanOrderActionType**](OrderActionRatePlanOrderActionType.md) |  | [optional] 
**update_product** | [**OrderActionRatePlanUpdate**](OrderActionRatePlanUpdate.md) |  | [optional] 
**sequence** | **int** | The sequence of the order actions processed in the order. | [optional] 

## Example

```python
from zuora_sdk.models.order_action_rate_plan_order_action import OrderActionRatePlanOrderAction

# TODO update the JSON string below
json = "{}"
# create an instance of OrderActionRatePlanOrderAction from a JSON string
order_action_rate_plan_order_action_instance = OrderActionRatePlanOrderAction.from_json(json)
# print the JSON string representation of the object
print(OrderActionRatePlanOrderAction.to_json())

# convert the object into a dict
order_action_rate_plan_order_action_dict = order_action_rate_plan_order_action_instance.to_dict()
# create an instance of OrderActionRatePlanOrderAction from a dict
order_action_rate_plan_order_action_from_dict = OrderActionRatePlanOrderAction.from_dict(order_action_rate_plan_order_action_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


