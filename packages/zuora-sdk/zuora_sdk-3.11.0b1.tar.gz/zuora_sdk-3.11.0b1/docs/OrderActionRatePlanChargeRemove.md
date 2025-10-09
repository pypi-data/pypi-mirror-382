# OrderActionRatePlanChargeRemove

The JSON object containing the information for a charge update(custom fields only) in the 'RemoveProduct' type order action. A custom field of rate plan charge can be updated from a subscription through one order action.  - If you update customFields of a charge while removing a rate plan, specify the following fields:   - `chargeNumber`   - `productRatePlanChargeId`   - `productRatePlanNumber`   - `uniqueToken`   - `customFields`

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**charge_number** | **str** | Read only. Identifies the charge to be updated.  | [optional] 
**product_rate_plan_charge_id** | **str** | Identifier of the rate plan that was updated.  | [optional] 
**product_rate_plan_number** | **str** | Number of a product rate plan for this subscription.  | [optional] 
**unique_token** | **str** | A unique string to represent the rate plan charge in the order. The unique token is used to perform multiple actions against a newly added rate plan. For example, if you want to add and update a product in the same order, you would assign a unique token to the product rate plan when added and use that token in future order actions. | [optional] 
**custom_fields** | **Dict[str, object]** | Container for custom fields of a Rate Plan Charge object.  | [optional] 

## Example

```python
from zuora_sdk.models.order_action_rate_plan_charge_remove import OrderActionRatePlanChargeRemove

# TODO update the JSON string below
json = "{}"
# create an instance of OrderActionRatePlanChargeRemove from a JSON string
order_action_rate_plan_charge_remove_instance = OrderActionRatePlanChargeRemove.from_json(json)
# print the JSON string representation of the object
print(OrderActionRatePlanChargeRemove.to_json())

# convert the object into a dict
order_action_rate_plan_charge_remove_dict = order_action_rate_plan_charge_remove_instance.to_dict()
# create an instance of OrderActionRatePlanChargeRemove from a dict
order_action_rate_plan_charge_remove_from_dict = OrderActionRatePlanChargeRemove.from_dict(order_action_rate_plan_charge_remove_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


