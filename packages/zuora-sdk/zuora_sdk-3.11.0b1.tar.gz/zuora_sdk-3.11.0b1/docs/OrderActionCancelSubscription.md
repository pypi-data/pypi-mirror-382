# OrderActionCancelSubscription

Information about an order action of type `CancelSubscription`. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**cancellation_effective_date** | **date** |  | [optional] 
**cancellation_policy** | [**SubscriptionCancellationPolicy**](SubscriptionCancellationPolicy.md) |  | 

## Example

```python
from zuora_sdk.models.order_action_cancel_subscription import OrderActionCancelSubscription

# TODO update the JSON string below
json = "{}"
# create an instance of OrderActionCancelSubscription from a JSON string
order_action_cancel_subscription_instance = OrderActionCancelSubscription.from_json(json)
# print the JSON string representation of the object
print(OrderActionCancelSubscription.to_json())

# convert the object into a dict
order_action_cancel_subscription_dict = order_action_cancel_subscription_instance.to_dict()
# create an instance of OrderActionCancelSubscription from a dict
order_action_cancel_subscription_from_dict = OrderActionCancelSubscription.from_dict(order_action_cancel_subscription_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


