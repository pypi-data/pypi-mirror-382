# OrderActionRatePlanChargeModelDataOverride

Container for charge model configuration data.   **Note**: This field is only available if you have the High Water Mark, Pre-Rated Pricing, or Multi-Attribute Pricing charge models enabled. The charge models are available for customers with Enterprise and Nine editions by default. If you are a Growth customer, see [Zuora Editions](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/C_Zuora_Editions) for pricing information.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**charge_model_configuration** | [**ChargeModelConfigurationForSubscription**](ChargeModelConfigurationForSubscription.md) |  | [optional] 
**tiers** | [**List[ChargeTier]**](ChargeTier.md) | List of cumulative pricing tiers in the charge.   **Note**: When you override tiers of the charge with a High Water Mark Pricing charge model, you have to provide all of the tiers, including the ones you do not want to change. The new tiers will completely override the previous ones. The High Water Mark Pricing charge models are available for customers with Enterprise and Nine editions by default. If you are a Growth customer, see [Zuora Editions](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/C_Zuora_Editions) for pricing information. | [optional] 

## Example

```python
from zuora_sdk.models.order_action_rate_plan_charge_model_data_override import OrderActionRatePlanChargeModelDataOverride

# TODO update the JSON string below
json = "{}"
# create an instance of OrderActionRatePlanChargeModelDataOverride from a JSON string
order_action_rate_plan_charge_model_data_override_instance = OrderActionRatePlanChargeModelDataOverride.from_json(json)
# print the JSON string representation of the object
print(OrderActionRatePlanChargeModelDataOverride.to_json())

# convert the object into a dict
order_action_rate_plan_charge_model_data_override_dict = order_action_rate_plan_charge_model_data_override_instance.to_dict()
# create an instance of OrderActionRatePlanChargeModelDataOverride from a dict
order_action_rate_plan_charge_model_data_override_from_dict = OrderActionRatePlanChargeModelDataOverride.from_dict(order_action_rate_plan_charge_model_data_override_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


