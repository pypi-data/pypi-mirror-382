# OrderActionRatePlanRecurringDeliveryPricingOverride

Pricing information about a recurring charge that uses the Delivery Pricing charge model. In this charge model, the charge has a fixed price. This field is only available if you have the Delivery Pricing charge model enabled.   **Note**: The Delivery Pricing charge model is in the **Early Adopter** phase. We are actively soliciting feedback from a small set of early adopters before releasing it as generally available. If you want to join this early adopter program, submit a request at <a href=\"http://support.zuora.com/\" target=\"_blank\">Zuora Global Support</a>.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**price_change_option** | [**PriceChangeOption**](PriceChangeOption.md) |  | [optional] [default to PriceChangeOption.NOCHANGE]
**price_increase_percentage** | **float** | Specifies the percentage by which the price of the charge should change each time the subscription renews. Only applicable if the value of the &#x60;priceChangeOption&#x60; field is &#x60;SpecificPercentageValue&#x60;.  | [optional] 
**delivery_schedule** | [**DeliveryScheduleParams**](DeliveryScheduleParams.md) |  | [optional] 
**list_price** | **float** | Price of the charge in each recurring period.  | [optional] 

## Example

```python
from zuora_sdk.models.order_action_rate_plan_recurring_delivery_pricing_override import OrderActionRatePlanRecurringDeliveryPricingOverride

# TODO update the JSON string below
json = "{}"
# create an instance of OrderActionRatePlanRecurringDeliveryPricingOverride from a JSON string
order_action_rate_plan_recurring_delivery_pricing_override_instance = OrderActionRatePlanRecurringDeliveryPricingOverride.from_json(json)
# print the JSON string representation of the object
print(OrderActionRatePlanRecurringDeliveryPricingOverride.to_json())

# convert the object into a dict
order_action_rate_plan_recurring_delivery_pricing_override_dict = order_action_rate_plan_recurring_delivery_pricing_override_instance.to_dict()
# create an instance of OrderActionRatePlanRecurringDeliveryPricingOverride from a dict
order_action_rate_plan_recurring_delivery_pricing_override_from_dict = OrderActionRatePlanRecurringDeliveryPricingOverride.from_dict(order_action_rate_plan_recurring_delivery_pricing_override_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


