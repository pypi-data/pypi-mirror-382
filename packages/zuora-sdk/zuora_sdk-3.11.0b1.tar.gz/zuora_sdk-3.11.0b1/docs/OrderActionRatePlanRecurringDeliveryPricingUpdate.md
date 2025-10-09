# OrderActionRatePlanRecurringDeliveryPricingUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**price_change_option** | [**PriceChangeOption**](PriceChangeOption.md) |  | [optional] [default to PriceChangeOption.NOCHANGE]
**price_increase_percentage** | **float** | Specifies the percentage by which the price of the charge should change each time the subscription renews. Only applicable if the value of the &#x60;priceChangeOption&#x60; field is &#x60;SpecificPercentageValue&#x60;.  | [optional] 
**delivery_schedule** | [**DeliveryScheduleParams**](DeliveryScheduleParams.md) |  | [optional] 
**list_price** | **float** |  | [optional] 

## Example

```python
from zuora_sdk.models.order_action_rate_plan_recurring_delivery_pricing_update import OrderActionRatePlanRecurringDeliveryPricingUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of OrderActionRatePlanRecurringDeliveryPricingUpdate from a JSON string
order_action_rate_plan_recurring_delivery_pricing_update_instance = OrderActionRatePlanRecurringDeliveryPricingUpdate.from_json(json)
# print the JSON string representation of the object
print(OrderActionRatePlanRecurringDeliveryPricingUpdate.to_json())

# convert the object into a dict
order_action_rate_plan_recurring_delivery_pricing_update_dict = order_action_rate_plan_recurring_delivery_pricing_update_instance.to_dict()
# create an instance of OrderActionRatePlanRecurringDeliveryPricingUpdate from a dict
order_action_rate_plan_recurring_delivery_pricing_update_from_dict = OrderActionRatePlanRecurringDeliveryPricingUpdate.from_dict(order_action_rate_plan_recurring_delivery_pricing_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


