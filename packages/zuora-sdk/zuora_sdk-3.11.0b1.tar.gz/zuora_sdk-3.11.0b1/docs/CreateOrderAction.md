# CreateOrderAction


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**create_subscription** | [**CreateOrderCreateSubscription**](CreateOrderCreateSubscription.md) |  | [optional] 
**add_product** | [**CreateOrderAddProduct**](CreateOrderAddProduct.md) |  | [optional] 
**update_product** | [**CreateOrderUpdateProduct**](CreateOrderUpdateProduct.md) |  | [optional] 
**change_plan** | [**CreateOrderChangePlan**](CreateOrderChangePlan.md) |  | [optional] 
**owner_transfer** | [**OrderActionOwnerTransfer**](OrderActionOwnerTransfer.md) |  | [optional] 
**remove_product** | [**OrderActionRemoveProduct**](OrderActionRemoveProduct.md) |  | [optional] 
**renew_subscription** | [**OrderActionRenewSubscription**](OrderActionRenewSubscription.md) |  | [optional] 
**cancel_subscription** | [**OrderActionCancelSubscription**](OrderActionCancelSubscription.md) |  | [optional] 
**resume** | [**CreateOrderResume**](CreateOrderResume.md) |  | [optional] 
**suspend** | [**CreateOrderSuspend**](CreateOrderSuspend.md) |  | [optional] 
**terms_and_conditions** | [**CreateOrderTermsAndConditions**](CreateOrderTermsAndConditions.md) |  | [optional] 
**change_reason** | **str** | The change reason set for an order action when an order is created.  | [optional] 
**trigger_dates** | [**List[TriggerDate]**](TriggerDate.md) | Container for the contract effective, service activation, and customer acceptance dates of the order action.   If [Zuora is configured to require service activation](https://knowledgecenter.zuora.com/CB_Billing/Billing_Settings/Define_Default_Subscription_Settings#Require_Service_Activation_of_Orders.3F) and the &#x60;ServiceActivation&#x60; field is not set for a &#x60;CreateSubscription&#x60; order action, a &#x60;Pending&#x60; order and a &#x60;Pending Activation&#x60; subscription are created.   If [Zuora is configured to require customer acceptance](https://knowledgecenter.zuora.com/CB_Billing/Billing_Settings/Define_Default_Subscription_Settings#Require_Customer_Acceptance_of_Orders.3F) and the &#x60;CustomerAcceptance&#x60; field is not set for a &#x60;CreateSubscription&#x60; order action, a &#x60;Pending&#x60; order and a &#x60;Pending Acceptance&#x60; subscription are created. At the same time, if the service activation date field is also required and not set, a &#x60;Pending&#x60; order and a &#x60;Pending Activation&#x60; subscription are created instead.  If [Zuora is configured to require service activation](https://knowledgecenter.zuora.com/CB_Billing/Billing_Settings/Define_Default_Subscription_Settings#Require_Service_Activation_of_Orders.3F) and the &#x60;ServiceActivation&#x60; field is not set for either of the following order actions, a &#x60;Pending&#x60; order is created. The subscription status is not impacted. **Note:** This feature is in **Limited Availability**. If you want to have access to the feature, submit a request at [Zuora Global Support](http://support.zuora.com/).  * AddProduct  * UpdateProduct  * RemoveProduct  * RenewSubscription  * TermsAndConditions   If [Zuora is configured to require customer acceptance](https://knowledgecenter.zuora.com/CB_Billing/Billing_Settings/Define_Default_Subscription_Settings#Require_Customer_Acceptance_of_Orders.3F) and the &#x60;CustomerAcceptance&#x60; field is not set for either of the following order actions, a &#x60;Pending&#x60; order is created. The subscription status is not impacted. **Note:** This feature is in **Limited Availability**. If you want to have access to the feature, submit a request at [Zuora Global Support](http://support.zuora.com/).  * AddProduct  * UpdateProduct  * RemoveProduct  * RenewSubscription  * TermsAndConditions  | [optional] 
**type** | [**OrderActionType**](OrderActionType.md) |  | 
**custom_fields** | **Dict[str, object]** | Container for custom fields of an Order Action object.  | [optional] 

## Example

```python
from zuora_sdk.models.create_order_action import CreateOrderAction

# TODO update the JSON string below
json = "{}"
# create an instance of CreateOrderAction from a JSON string
create_order_action_instance = CreateOrderAction.from_json(json)
# print the JSON string representation of the object
print(CreateOrderAction.to_json())

# convert the object into a dict
create_order_action_dict = create_order_action_instance.to_dict()
# create an instance of CreateOrderAction from a dict
create_order_action_from_dict = CreateOrderAction.from_dict(create_order_action_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


