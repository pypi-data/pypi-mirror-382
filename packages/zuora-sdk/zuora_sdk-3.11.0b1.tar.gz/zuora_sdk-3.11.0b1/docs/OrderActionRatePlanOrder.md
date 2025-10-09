# OrderActionRatePlanOrder

The order that is related to the subscription rate plan. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The order ID. | [optional] 
**order_actions** | [**List[OrderActionRatePlanOrderAction]**](OrderActionRatePlanOrderAction.md) |  | [optional] 
**order_number** | **str** | The order number of the order. | [optional] 

## Example

```python
from zuora_sdk.models.order_action_rate_plan_order import OrderActionRatePlanOrder

# TODO update the JSON string below
json = "{}"
# create an instance of OrderActionRatePlanOrder from a JSON string
order_action_rate_plan_order_instance = OrderActionRatePlanOrder.from_json(json)
# print the JSON string representation of the object
print(OrderActionRatePlanOrder.to_json())

# convert the object into a dict
order_action_rate_plan_order_dict = order_action_rate_plan_order_instance.to_dict()
# create an instance of OrderActionRatePlanOrder from a dict
order_action_rate_plan_order_from_dict = OrderActionRatePlanOrder.from_dict(order_action_rate_plan_order_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


