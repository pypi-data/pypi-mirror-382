# OrderActionRatePlanChargeOverride

Charge associated with a rate plan. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**billing** | [**ChargeOverrideBilling**](ChargeOverrideBilling.md) |  | [optional] 
**charge_number** | **str** | Charge number of the charge. For example, C-00000307.  If you do not set this field, Zuora will generate the charge number.  | [optional] 
**custom_fields** | **Dict[str, object]** | Container for custom fields of a Rate Plan Charge object.  | [optional] 
**description** | **str** | Description of the charge.  | [optional] 
**end_date** | [**EndConditions**](EndConditions.md) |  | [optional] 
**pricing** | [**RatePlanChargeOverridePricing**](RatePlanChargeOverridePricing.md) |  | [optional] 
**product_rate_plan_charge_id** | **str** | Internal identifier of the product rate plan charge that the charge is based on.  | 
**rev_rec_code** | **str** | Revenue Recognition Code  | [optional] 
**rev_rec_trigger_condition** | [**RevRecTriggerCondition**](RevRecTriggerCondition.md) |  | [optional] 
**revenue_recognition_rule_name** | [**RevenueRecognitionRuleName**](RevenueRecognitionRuleName.md) |  | [optional] 
**start_date** | [**TriggerParams**](TriggerParams.md) |  | [optional] 
**estimated_start_date** | **date** | **Note**: This field is only available if you have the [Pending Charge Flexibility] (https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Pending_Charge_Flexibility). feature enabled. Estimated Start Date of the charge. | [optional] 
**unique_token** | **str** | Unique identifier for the charge. This identifier enables you to refer to the charge before the charge has an internal identifier in Zuora.  For instance, suppose that you want to use a single order to add a product to a subscription and later update the same product. When you add the product, you can set a unique identifier for the charge. Then when you update the product, you can use the same unique identifier to specify which charge to modify.  | [optional] 

## Example

```python
from zuora_sdk.models.order_action_rate_plan_charge_override import OrderActionRatePlanChargeOverride

# TODO update the JSON string below
json = "{}"
# create an instance of OrderActionRatePlanChargeOverride from a JSON string
order_action_rate_plan_charge_override_instance = OrderActionRatePlanChargeOverride.from_json(json)
# print the JSON string representation of the object
print(OrderActionRatePlanChargeOverride.to_json())

# convert the object into a dict
order_action_rate_plan_charge_override_dict = order_action_rate_plan_charge_override_instance.to_dict()
# create an instance of OrderActionRatePlanChargeOverride from a dict
order_action_rate_plan_charge_override_from_dict = OrderActionRatePlanChargeOverride.from_dict(order_action_rate_plan_charge_override_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


