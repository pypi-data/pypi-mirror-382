# CreateOrderResponseSubscriptions


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**CreateOrderResponseSubscriptionStatus**](CreateOrderResponseSubscriptionStatus.md) |  | [optional] 
**subscription_id** | **str** | Subscription ID of the subscription included in this order. This field is returned instead of the &#x60;subscriptionNumber&#x60; field if the &#x60;returnIds&#x60; query parameter is set to &#x60;true&#x60;. | [optional] 
**subscription_number** | **str** | Subscription number of the subscription included in this order. | [optional] 
**subscription_owner_id** | **str** | subscription owner account id of the subscription | [optional] 
**subscription_owner_number** | **str** | subscription owner account number of the subscription | [optional] 
**order_actions** | [**List[CreateOrderResponseOrderAction]**](CreateOrderResponseOrderAction.md) | subscription order action metrics | [optional] 

## Example

```python
from zuora_sdk.models.create_order_response_subscriptions import CreateOrderResponseSubscriptions

# TODO update the JSON string below
json = "{}"
# create an instance of CreateOrderResponseSubscriptions from a JSON string
create_order_response_subscriptions_instance = CreateOrderResponseSubscriptions.from_json(json)
# print the JSON string representation of the object
print(CreateOrderResponseSubscriptions.to_json())

# convert the object into a dict
create_order_response_subscriptions_dict = create_order_response_subscriptions_instance.to_dict()
# create an instance of CreateOrderResponseSubscriptions from a dict
create_order_response_subscriptions_from_dict = CreateOrderResponseSubscriptions.from_dict(create_order_response_subscriptions_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


