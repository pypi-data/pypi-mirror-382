# OrderActionRatePlanChargeUpdate

The JSON object containing the information for a charge update in the 'UpdateProduct' type order action.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**billing** | [**OrderActionRatePlanBillingUpdate**](OrderActionRatePlanBillingUpdate.md) | Billing information about the charge.  | [optional] 
**charge_number** | **str** | Read only. Identifies the charge to be updated.  | [optional] 
**custom_fields** | **Dict[str, object]** | Container for custom fields of a Rate Plan Charge object.  | [optional] 
**description** | **str** | Description of the charge.  | [optional] 
**effective_date** | [**TriggerParams**](TriggerParams.md) |  | [optional] 
**estimated_start_date** | **date** | **Note**: This field is only available if you have the [Pending Charge Flexibility] (https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Pending_Charge_Flexibility). feature enabled. Estimated Start Date of the charge. | [optional] 
**pricing** | [**OrderActionRatePlanPricingUpdate**](OrderActionRatePlanPricingUpdate.md) | Pricing information about the charge.  | [optional] 
**unique_token** | **str** | A unique string to represent the rate plan charge in the order. The unique token is used to perform multiple actions against a newly added rate plan. For example, if you want to add and update a product in the same order, you would assign a unique token to the product rate plan when added and use that token in future order actions. | [optional] 

## Example

```python
from zuora_sdk.models.order_action_rate_plan_charge_update import OrderActionRatePlanChargeUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of OrderActionRatePlanChargeUpdate from a JSON string
order_action_rate_plan_charge_update_instance = OrderActionRatePlanChargeUpdate.from_json(json)
# print the JSON string representation of the object
print(OrderActionRatePlanChargeUpdate.to_json())

# convert the object into a dict
order_action_rate_plan_charge_update_dict = order_action_rate_plan_charge_update_instance.to_dict()
# create an instance of OrderActionRatePlanChargeUpdate from a dict
order_action_rate_plan_charge_update_from_dict = OrderActionRatePlanChargeUpdate.from_dict(order_action_rate_plan_charge_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


