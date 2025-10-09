# OrderActionRatePlanRecurringFlatFeePricingOverride

Pricing information about a recurring charge that uses the \"flat fee\" charge model. In this charge model, the charge has a fixed price.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**price_change_option** | [**PriceChangeOption**](PriceChangeOption.md) |  | [optional] [default to PriceChangeOption.NOCHANGE]
**price_increase_percentage** | **float** | Specifies the percentage by which the price of the charge should change each time the subscription renews. Only applicable if the value of the &#x60;priceChangeOption&#x60; field is &#x60;SpecificPercentageValue&#x60;.  | [optional] 
**list_price** | **float** | Price of the charge in each recurring period.  | [optional] 
**list_price_base** | [**ChargeListPriceBase**](ChargeListPriceBase.md) |  | [optional] 
**specific_list_price_base** | **int** | The number of months for the list price base of the charge. The value of this field is &#x60;null&#x60; if you do not set the value of the &#x60;listPriceBase&#x60; field to &#x60;Per_Specific_Months&#x60;. | [optional] 

## Example

```python
from zuora_sdk.models.order_action_rate_plan_recurring_flat_fee_pricing_override import OrderActionRatePlanRecurringFlatFeePricingOverride

# TODO update the JSON string below
json = "{}"
# create an instance of OrderActionRatePlanRecurringFlatFeePricingOverride from a JSON string
order_action_rate_plan_recurring_flat_fee_pricing_override_instance = OrderActionRatePlanRecurringFlatFeePricingOverride.from_json(json)
# print the JSON string representation of the object
print(OrderActionRatePlanRecurringFlatFeePricingOverride.to_json())

# convert the object into a dict
order_action_rate_plan_recurring_flat_fee_pricing_override_dict = order_action_rate_plan_recurring_flat_fee_pricing_override_instance.to_dict()
# create an instance of OrderActionRatePlanRecurringFlatFeePricingOverride from a dict
order_action_rate_plan_recurring_flat_fee_pricing_override_from_dict = OrderActionRatePlanRecurringFlatFeePricingOverride.from_dict(order_action_rate_plan_recurring_flat_fee_pricing_override_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


