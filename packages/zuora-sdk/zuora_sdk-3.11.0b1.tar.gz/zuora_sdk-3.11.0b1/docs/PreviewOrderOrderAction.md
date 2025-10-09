# PreviewOrderOrderAction


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**add_product** | [**PreviewOrderRatePlanOverride**](PreviewOrderRatePlanOverride.md) |  | [optional] 
**cancel_subscription** | [**OrderActionCancelSubscription**](OrderActionCancelSubscription.md) |  | [optional] 
**change_plan** | [**CreateOrderChangePlan**](CreateOrderChangePlan.md) |  | [optional] 
**change_reason** | **str** | The change reason set for an order action when an order is created.  | [optional] 
**create_subscription** | [**PreviewOrderCreateSubscription**](PreviewOrderCreateSubscription.md) |  | [optional] 
**custom_fields** | **Dict[str, object]** | Container for custom fields of an Order Action object.  | [optional] 
**owner_transfer** | [**OrderActionOwnerTransfer**](OrderActionOwnerTransfer.md) |  | [optional] 
**remove_product** | [**OrderActionRemoveProduct**](OrderActionRemoveProduct.md) |  | [optional] 
**renew_subscription** | [**OrderActionRenewSubscription**](OrderActionRenewSubscription.md) |  | [optional] 
**resume** | [**CreateOrderResume**](CreateOrderResume.md) |  | [optional] 
**suspend** | [**CreateOrderSuspend**](CreateOrderSuspend.md) |  | [optional] 
**terms_and_conditions** | [**CreateOrderTermsAndConditions**](CreateOrderTermsAndConditions.md) |  | [optional] 
**trigger_dates** | [**List[TriggerDate]**](TriggerDate.md) | Container for the contract effective, service activation, and customer acceptance dates of the order action.   If the service activation date is set as a required field in Default Subscription Settings, skipping this field in a &#x60;CreateSubscription&#x60; order action of your JSON request will result in a &#x60;Pending&#x60; order and a &#x60;Pending Activation&#x60; subscription.  If the customer acceptance date is set as a required field in Default Subscription Settings, skipping this field in a &#x60;CreateSubscription&#x60; order action of your JSON request will result in a &#x60;Pending&#x60; order and a &#x60;Pending Acceptance&#x60; subscription. If the service activation date field is at the same time required and skipped (or set as null), it will be a &#x60;Pending Activation&#x60; subscription.  | [optional] 
**type** | [**OrderActionType**](OrderActionType.md) |  | 
**update_product** | [**PreviewOrderRatePlanUpdate**](PreviewOrderRatePlanUpdate.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.preview_order_order_action import PreviewOrderOrderAction

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewOrderOrderAction from a JSON string
preview_order_order_action_instance = PreviewOrderOrderAction.from_json(json)
# print the JSON string representation of the object
print(PreviewOrderOrderAction.to_json())

# convert the object into a dict
preview_order_order_action_dict = preview_order_order_action_instance.to_dict()
# create an instance of PreviewOrderOrderAction from a dict
preview_order_order_action_from_dict = PreviewOrderOrderAction.from_dict(preview_order_order_action_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


