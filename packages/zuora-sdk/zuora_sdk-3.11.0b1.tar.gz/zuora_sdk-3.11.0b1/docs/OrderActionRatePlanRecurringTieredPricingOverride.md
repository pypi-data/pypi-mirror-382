# OrderActionRatePlanRecurringTieredPricingOverride

Pricing information about a recurring charge that uses the \"tiered pricing\" charge model. In this charge model, the charge has cumulative pricing tiers that become effective as units are purchased.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**price_change_option** | [**PriceChangeOption**](PriceChangeOption.md) |  | [optional] [default to PriceChangeOption.NOCHANGE]
**price_increase_percentage** | **float** | Specifies the percentage by which the price of the charge should change each time the subscription renews. Only applicable if the value of the &#x60;priceChangeOption&#x60; field is &#x60;SpecificPercentageValue&#x60;.  | [optional] 
**list_price_base** | [**ChargeListPriceBase**](ChargeListPriceBase.md) |  | [optional] 
**quantity** | **float** | Number of units purchased.  | [optional] 
**specific_list_price_base** | **int** | The number of months for the list price base of the charge. This field is required if you set the value of the &#x60;listPriceBase&#x60; field to &#x60;Per_Specific_Months&#x60;. | [optional] 
**tiers** | [**List[ChargeTier]**](ChargeTier.md) | List of cumulative pricing tiers in the charge.  | [optional] 

## Example

```python
from zuora_sdk.models.order_action_rate_plan_recurring_tiered_pricing_override import OrderActionRatePlanRecurringTieredPricingOverride

# TODO update the JSON string below
json = "{}"
# create an instance of OrderActionRatePlanRecurringTieredPricingOverride from a JSON string
order_action_rate_plan_recurring_tiered_pricing_override_instance = OrderActionRatePlanRecurringTieredPricingOverride.from_json(json)
# print the JSON string representation of the object
print(OrderActionRatePlanRecurringTieredPricingOverride.to_json())

# convert the object into a dict
order_action_rate_plan_recurring_tiered_pricing_override_dict = order_action_rate_plan_recurring_tiered_pricing_override_instance.to_dict()
# create an instance of OrderActionRatePlanRecurringTieredPricingOverride from a dict
order_action_rate_plan_recurring_tiered_pricing_override_from_dict = OrderActionRatePlanRecurringTieredPricingOverride.from_dict(order_action_rate_plan_recurring_tiered_pricing_override_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


