# ChangeSubscriptionRatePlan


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**booking_date** | **date** | The booking date that you want to set for the amendment contract. The booking date of an amendment is the equivalent of the order date of an order. This field must be in the &#x60;yyyy-mm-dd&#x60; format. The default value is the current date when you make the API call.   | [optional] 
**charge_overrides** | [**List[AddSubscriptionComponent]**](AddSubscriptionComponent.md) | This optional container is used to override one or more product rate plan charges for this subscription. | [optional] 
**contract_effective_date** | **date** | Effective date of the new subscription, as yyyy-mm-dd. | [optional] 
**customer_acceptance_date** | **date** | The date when the customer accepts the contract in yyyy-mm-dd format. When this field is not set: * If the &#x60;serviceActivationDate&#x60; field is not set, the value of this field is set to be the contract effective date. * If the &#x60;serviceActivationDate&#x60; field is set, the value of this field is set to be the service activation date.  The billing trigger dates must follow this rule: contractEffectiveDate &lt;&#x3D; serviceActivationDate &lt;&#x3D; contractAcceptanceDate  | [optional] 
**effective_policy** | **str** | The default value for the &#x60;effectivePolicy&#x60; field is as follows:   * If the rate plan change (from old to new) is an upgrade, the effective policy is &#x60;EffectiveImmediately&#x60; by default.   * If the rate plan change (from old to new) is a downgrade, the effective policy is &#x60;EffectiveEndOfBillingPeriod&#x60; by default.   * Otherwise, the effective policy is &#x60;SpecificDate&#x60; by default.  Note that if the &#x60;effectivePolicy&#x60; field is set to &#x60;EffectiveEndOfBillingPeriod&#x60;, you cannot set the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Subscriptions/Subscriptions/W_Subscription_and_Amendment_Dates#Billing_Trigger_Dates\&quot; target&#x3D;\&quot;_blank\&quot;&gt;billing trigger dates&lt;/a&gt; for the subscription as the system will automatically set the trigger dates to the end of billing period.  | [optional] 
**external_catalog_plan_id** | **str** | An external ID of the rate plan to be removed. You can use this field to specify an existing rate plan in your subscription. The value of the &#x60;externalCatalogPlanId&#x60; field must match one of the values that are predefined in the &#x60;externallyManagedPlanIds&#x60; field on a product rate plan. However, if there are multiple rate plans with the same &#x60;productRatePlanId&#x60; value existing in the subscription, you must use the &#x60;ratePlanId&#x60; field to remove the rate plan. The &#x60;externalCatalogPlanId&#x60; field cannot be used to distinguish multiple rate plans in this case.  **Note:** Provide only one of &#x60;externalCatalogPlanId&#x60;, &#x60;ratePlanId&#x60; or &#x60;productRatePlanId&#x60;. If more than one field is provided then the request would fail.  | [optional] 
**external_id_source_system** | **str** | The ID of the external source system. You can use this field and &#x60;externalCatalogPlanId&#x60; to specify a product rate plan that is imported from an external system.  **Note:** If both &#x60;externalCatalogPlanId&#x60;, &#x60;externalIdSourceSystem&#x60; and &#x60;productRatePlanId&#x60; are provided. They must point to the same product rate plan. Otherwise, the request would fail.  | [optional] 
**new_external_catalog_plan_id** | **str** | An external ID of the product rate plan to be added. You can use this field to specify a product rate plan that is imported from an external system. The value of the &#x60;externalCatalogPlanId&#x60; field must match one of the values that are predefined in the &#x60;externallyManagedPlanIds&#x60; field on a product rate plan.  **Note:** Provide only one of &#x60;newExternalCatalogPlanId&#x60; or &#x60;newProductRatePlanId&#x60;. If both fields are provided then the request would fail.  | [optional] 
**new_external_id_source_system** | **str** | The ID of the external source system. You can use this field and &#x60;newExternalCatalogPlanId&#x60; to specify a product rate plan that is imported from an external system.  **Note:** If both &#x60;newExternalCatalogPlanId&#x60;, &#x60;newExternalIdSourceSystem&#x60; and &#x60;newProductRatePlanId&#x60; are provided. They must point to the same product rate plan. Otherwise, the request would fail.  | [optional] 
**new_product_rate_plan_id** | **str** | ID of a product rate plan for this subscription. | [optional] 
**new_product_rate_plan_number** | **str** | Number of a product rate plan for this subscription. | [optional] 
**product_rate_plan_id** | **str** | ID of the product rate plan that the removed rate plan is based on.  | [optional] 
**product_rate_plan_number** | **str** | Number of a product rate plan for this subscription.     | [optional] 
**rate_plan_id** | **str** | ID of a rate plan to remove. Note that the removal of a rate plan through the Change Plan amendment supports the function of &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Subscriptions/Subscriptions/Subscribe_and_Amend/E_Amendments/EB_Remove_rate_plan_on_subscription_before_future-dated_removals\&quot; target&#x3D;\&quot;_blank\&quot;&gt;removal before future-dated removals&lt;/a&gt;, as in a Remove Product amendment.  | [optional] 
**reset_bcd** | **bool** | If resetBcd is true then reset the Account BCD to the effective date; if it is false keep the original BCD.  | [optional] [default to False]
**service_activation_date** | **date** | The date when the change in the subscription is activated in yyyy-mm-dd format. You must specify a Service Activation date if the Customer Acceptance date is set. If the Customer Acceptance date is not set, the value of the &#x60;serviceActivationDate&#x60; field defaults to be the Contract Effective Date. The billing trigger dates must follow this rule: contractEffectiveDate &lt;&#x3D; serviceActivationDate &lt;&#x3D; contractAcceptanceDate | [optional] 
**sub_type** | **str** | Use this field to choose the sub type for your change plan amendment.   However, if you do not set this field, the field will be automatically generated by the system according to the following rules:  When the old and new rate plans are within the same Grading catalog group: * If the grade of new plan is greater than that of the old plan, this is an \&quot;Upgrade\&quot;. * If the grade of new plan is less than that of the old plan, this is a \&quot;Downgrade\&quot;. * If the grade of new plan equals that of the old plan, this is a \&quot;Crossgrade\&quot;.  When the old and new rate plans are not in the same Grading catalog group, or either has no group, this is \&quot;PlanChanged\&quot;.  | [optional] 
**subscription_rate_plan_number** | **str** | Number of a rate plan for this subscription.   | [optional] 

## Example

```python
from zuora_sdk.models.change_subscription_rate_plan import ChangeSubscriptionRatePlan

# TODO update the JSON string below
json = "{}"
# create an instance of ChangeSubscriptionRatePlan from a JSON string
change_subscription_rate_plan_instance = ChangeSubscriptionRatePlan.from_json(json)
# print the JSON string representation of the object
print(ChangeSubscriptionRatePlan.to_json())

# convert the object into a dict
change_subscription_rate_plan_dict = change_subscription_rate_plan_instance.to_dict()
# create an instance of ChangeSubscriptionRatePlan from a dict
change_subscription_rate_plan_from_dict = ChangeSubscriptionRatePlan.from_dict(change_subscription_rate_plan_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


