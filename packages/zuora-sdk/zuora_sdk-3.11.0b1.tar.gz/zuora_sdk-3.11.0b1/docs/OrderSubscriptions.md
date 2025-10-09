# OrderSubscriptions


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**base_version** | **int** | The base version of the subscription. | [optional] 
**custom_fields** | **Dict[str, object]** | Container for custom fields of a Subscription object.  | [optional] 
**externally_managed_by** | [**ExternallyManagedBy**](ExternallyManagedBy.md) |  | [optional] 
**new_version** | **int** | The latest version of the subscription. | [optional] 
**order_actions** | [**List[OrderAction]**](OrderAction.md) |  | [optional] 
**quote** | [**QuoteObjectFields**](QuoteObjectFields.md) |  | [optional] 
**notes** | **str** | A string of up to 65,535 characters.  | [optional] 
**ramp** | **object** | **Note**: This field is only available if you have the Ramps feature enabled. The [Orders](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/AA_Overview_of_Orders) feature must be enabled before you can access the [Ramps](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/Ramps_and_Ramp_Metrics/A_Overview_of_Ramps_and_Ramp_Metrics) feature. The Ramps feature is available for customers with Enterprise and Nine editions by default. If you are a Growth customer, see [Zuora Editions](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/C_Zuora_Editions) for pricing information coming October 2020.  The ramp definition.  | [optional] 
**sequence** | **int** | The sequence number of a certain subscription processed by the order. | [optional] 
**subscription_number** | **str** | The new subscription number for a new subscription created, or the existing subscription number. Unlike the order request, the subscription number here always has a value. | [optional] 
**subscription_owner_account_number** | **str** | The number of the account that owns the subscription. | [optional] 
**subscription_owner_account_details** | [**OrderSubscriptionsSubscriptionOwnerAccountDetails**](OrderSubscriptionsSubscriptionOwnerAccountDetails.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.order_subscriptions import OrderSubscriptions

# TODO update the JSON string below
json = "{}"
# create an instance of OrderSubscriptions from a JSON string
order_subscriptions_instance = OrderSubscriptions.from_json(json)
# print the JSON string representation of the object
print(OrderSubscriptions.to_json())

# convert the object into a dict
order_subscriptions_dict = order_subscriptions_instance.to_dict()
# create an instance of OrderSubscriptions from a dict
order_subscriptions_from_dict = OrderSubscriptions.from_dict(order_subscriptions_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


