# OrderActionRatePlanBillingUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**billing_period_alignment** | [**BillingPeriodAlignment**](BillingPeriodAlignment.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.order_action_rate_plan_billing_update import OrderActionRatePlanBillingUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of OrderActionRatePlanBillingUpdate from a JSON string
order_action_rate_plan_billing_update_instance = OrderActionRatePlanBillingUpdate.from_json(json)
# print the JSON string representation of the object
print(OrderActionRatePlanBillingUpdate.to_json())

# convert the object into a dict
order_action_rate_plan_billing_update_dict = order_action_rate_plan_billing_update_instance.to_dict()
# create an instance of OrderActionRatePlanBillingUpdate from a dict
order_action_rate_plan_billing_update_from_dict = OrderActionRatePlanBillingUpdate.from_dict(order_action_rate_plan_billing_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


