# CreateOrderChangePlan

Information about an order action of type `changePlan`.   Use the change plan type of order action to replace the existing rate plans in a subscription with other rate plans.  **Note**: The change plan type of order action is currently not supported for Billing - Revenue Integration. When Billing - Revenue Integration is enabled, the change plan type of order action will no longer be applicable in Zuora Billing.  If you want to create a pending order through the \"change plan\" order action, and if the charge's trigger condition is `Specific Date`, you must set a charge number in the `chargeNumber` field for the \"change plan\" order action. In this case, if you do not set it, Zuora will not generate the charge number for you.  See more information about pending orders in <a href=\"https://knowledgecenter.zuora.com/Zuora_Billing/Subscriptions/Subscriptions/Orders/AA_Overview_of_Orders/Pending_orders_and_subscriptions\" target=\"_blank\">Pending orders and subscriptions</a>. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**effective_policy** | [**ChangePlanEffectivePolicy**](ChangePlanEffectivePolicy.md) |  | [optional] 
**external_catalog_plan_id** | **str** | An external ID of the rate plan to be removed. You can use this field to specify an existing rate plan in your subscription. The value of the &#x60;externalCatalogPlanId&#x60; field must match one of the values that are predefined in the &#x60;externallyManagedPlanIds&#x60; field on a product rate plan. However, if there are multiple rate plans with the same &#x60;productRatePlanId&#x60; value existing in the subscription, you must use the &#x60;ratePlanId&#x60; field to remove the rate plan. The &#x60;externalCatalogPlanId&#x60; field cannot be used to distinguish multiple rate plans in this case.  **Note:** Please provide only one of &#x60;externalCatalogPlanId&#x60;, &#x60;ratePlanId&#x60; or &#x60;productRatePlanId&#x60;. If more than 1 field is provided then the request would fail.  | [optional] 
**new_product_rate_plan** | [**CreateOrderChangePlanRatePlanOverride**](CreateOrderChangePlanRatePlanOverride.md) |  | 
**product_rate_plan_id** | **str** | ID of the product rate plan that the removed rate plan is based on.  | [optional] 
**product_rate_plan_number** | **str** | Number of a product rate plan for this subscription.  | [optional] 
**rate_plan_id** | **str** | ID of the rate plan to remove. This can be the latest version or any history version of ID. Note that the removal of a rate plan through the Change Plan order action supports the function of &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Subscriptions/Subscriptions/Orders/Order_actions_tutorials/E2_Remove_rate_plan_on_subscription_before_future-dated_removals\&quot; target&#x3D;\&quot;_blank\&quot;&gt;removal before future-dated removals&lt;/a&gt;, as in a Remove Product order action.  | [optional] 
**reset_bcd** | **bool** | If resetBcd is true then reset the Account BCD to the effective date; if it is false keep the original BCD.  | [optional] [default to False]
**sub_type** | [**ChangePlanSubType**](ChangePlanSubType.md) |  | [optional] 
**subscription_rate_plan_number** | **str** | Number of a rate plan for this subscription.  | [optional] 

## Example

```python
from zuora_sdk.models.create_order_change_plan import CreateOrderChangePlan

# TODO update the JSON string below
json = "{}"
# create an instance of CreateOrderChangePlan from a JSON string
create_order_change_plan_instance = CreateOrderChangePlan.from_json(json)
# print the JSON string representation of the object
print(CreateOrderChangePlan.to_json())

# convert the object into a dict
create_order_change_plan_dict = create_order_change_plan_instance.to_dict()
# create an instance of CreateOrderChangePlan from a dict
create_order_change_plan_from_dict = CreateOrderChangePlan.from_dict(create_order_change_plan_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


