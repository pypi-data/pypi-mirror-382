# OrderActionRatePlanOverride

Rate plan associated with a subscription. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**charge_overrides** | [**List[OrderActionRatePlanChargeOverride]**](OrderActionRatePlanChargeOverride.md) | List of charges associated with the rate plan.  | [optional] 
**custom_fields** | **Dict[str, object]** | Container for custom fields of a Rate Plan object.  | [optional] 
**new_rate_plan_id** | **str** | Internal identifier of the rate plan.  | [optional] 
**product_rate_plan_id** | **str** | Internal identifier of the product rate plan that the rate plan is based on. | 
**unique_token** | **str** | Unique identifier for the rate plan. This identifier enables you to refer to the rate plan before the rate plan has an internal identifier in Zuora.   For instance, suppose that you want to use a single order to add a product to a subscription and later update the same product. When you add the product, you can set a unique identifier for the rate plan. Then when you update the product, you can use the same unique identifier to specify which rate plan to modify. | [optional] 

## Example

```python
from zuora_sdk.models.order_action_rate_plan_override import OrderActionRatePlanOverride

# TODO update the JSON string below
json = "{}"
# create an instance of OrderActionRatePlanOverride from a JSON string
order_action_rate_plan_override_instance = OrderActionRatePlanOverride.from_json(json)
# print the JSON string representation of the object
print(OrderActionRatePlanOverride.to_json())

# convert the object into a dict
order_action_rate_plan_override_dict = order_action_rate_plan_override_instance.to_dict()
# create an instance of OrderActionRatePlanOverride from a dict
order_action_rate_plan_override_from_dict = OrderActionRatePlanOverride.from_dict(order_action_rate_plan_override_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


