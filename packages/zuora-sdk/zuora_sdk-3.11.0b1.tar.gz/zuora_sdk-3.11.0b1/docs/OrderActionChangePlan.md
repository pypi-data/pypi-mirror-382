# OrderActionChangePlan

Information about an order action of type `ChangePlan`.  **Note**: The change plan type of order action is currently not supported for Billing - Revenue Integration. When Billing - Revenue Integration is enabled, the change plan type of order action will no longer be applicable in Zuora Billing. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**effective_policy** | [**ChangePlanEffectivePolicy**](ChangePlanEffectivePolicy.md) |  | [optional] 
**new_product_rate_plan** | [**ChangePlanRatePlanOverride**](ChangePlanRatePlanOverride.md) |  | [optional] 
**product_rate_plan_id** | **str** | ID of the rate plan to remove. This can be the latest version or any history version of ID.  | [optional] 
**product_rate_plan_number** | **str** | Number of a product rate plan for this subscription.  | [optional] 
**rate_plan_id** | **str** | ID of the rate plan to remove. This can be the latest version or any history version of ID.  | [optional] 
**sub_type** | [**ChangePlanSubType**](ChangePlanSubType.md) |  | [optional] 
**subscription_rate_plan_number** | **str** | Number of a rate plan for this subscription.  | [optional] 

## Example

```python
from zuora_sdk.models.order_action_change_plan import OrderActionChangePlan

# TODO update the JSON string below
json = "{}"
# create an instance of OrderActionChangePlan from a JSON string
order_action_change_plan_instance = OrderActionChangePlan.from_json(json)
# print the JSON string representation of the object
print(OrderActionChangePlan.to_json())

# convert the object into a dict
order_action_change_plan_dict = order_action_change_plan_instance.to_dict()
# create an instance of OrderActionChangePlan from a dict
order_action_change_plan_from_dict = OrderActionChangePlan.from_dict(order_action_change_plan_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


