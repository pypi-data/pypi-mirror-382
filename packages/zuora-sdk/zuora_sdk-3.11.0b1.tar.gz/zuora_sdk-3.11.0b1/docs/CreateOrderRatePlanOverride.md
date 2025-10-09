# CreateOrderRatePlanOverride

Information about an order action of type `addProduct`.    If you want to create a pending order through the \"Add product\" order action, and if the charge's trigger condition is `Specific Date`, you must set a charge number in the `chargeNumber` field for the \"Add product\" order action. In this case, if you do not set it, Zuora will not generate the charge number for you.   See more information about pending orders in <a href=\"https://knowledgecenter.zuora.com/Zuora_Billing/Subscriptions/Subscriptions/Orders/AA_Overview_of_Orders/Pending_orders_and_subscriptions\" target=\"_blank\">Pending orders and subscriptions</a>. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**charge_overrides** | [**List[ChargeOverride]**](ChargeOverride.md) | List of charges associated with the rate plan.  | [optional] 
**clearing_existing_features** | **bool** | Specifies whether all features in the rate plan will be cleared.  | [optional] 
**custom_fields** | **Dict[str, object]** | Container for custom fields of the Rate Plan object. The custom fields of the Rate Plan object are used when rate plans are subscribed. | [optional] 
**external_catalog_plan_id** | **str** | An external ID of the product rate plan to be added. You can use this field to specify a product rate plan that is imported from an external system. The value of the &#x60;externalCatalogPlanId&#x60; field must match one of the values that are predefined in the &#x60;externallyManagedPlanIds&#x60; field on a product rate plan.   **Note:** If both &#x60;externalCatalogPlanId&#x60; and &#x60;productRatePlanId&#x60; are provided. They must point to the same product rate plan. Otherwise, the request would fail. | [optional] 
**externally_managed_plan_id** | **str** | Indicates the unique identifier for the rate plan purchased on a third-party store. This field is used to represent a subscription rate plan created through third-party stores. | [optional] 
**product_rate_plan_id** | **str** | Internal identifier of the product rate plan that the rate plan is based on. | [optional] 
**product_rate_plan_number** | **str** | Number of a product rate plan for this subscription.  | [optional] 
**subscription_product_features** | [**List[CreateOrderRatePlanFeatureOverride]**](CreateOrderRatePlanFeatureOverride.md) | List of features associated with the rate plan.  The system compares the &#x60;subscriptionProductFeatures&#x60; and &#x60;featureId&#x60; fields in the request with the counterpart fields in a rate plan. The comparison results are as follows:  * If there is no &#x60;subscriptionProductFeatures&#x60; field or the field is empty, features in the rate plan remain unchanged. But if the &#x60;clearingExistingFeatures&#x60; field is additionally set to true, all features in the rate plan are cleared.  * If the &#x60;subscriptionProductFeatures&#x60; field contains the &#x60;featureId&#x60; nested fields, as well as the optional &#x60;description&#x60; and &#x60;customFields&#x60; nested fields, the features indicated by the featureId nested fields in the request overwrite all features in the rate plan. | [optional] 
**unique_token** | **str** | Unique identifier for the rate plan. This identifier enables you to refer to the rate plan before the rate plan has an internal identifier in Zuora.   For instance, suppose that you want to use a single order to add a product to a subscription and later update the same product. When you add the product, you can set a unique identifier for the rate plan. Then when you update the product, you can use the same unique identifier to specify which rate plan to modify. | [optional] 
**subscription_rate_plan_number** | **str** | Number of a subscription rate plan for this subscription.  | [optional] 
**is_from_external_catalog** | **bool** | Indicates whether the rate plan is created from the Zuora product catalog or from an external product catalog.  **Note:** This field is available when the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Manage_subscription_transactions/Orders/Standalone_Orders/AA_Overview_of_Standalone_Orders\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Standalone Orders&lt;/a&gt; feature is enabled.  | [optional] 
**rate_plan_name** | **str** | Name of the standalone rate plan.  **Note:** This field is available when the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Manage_subscription_transactions/Orders/Standalone_Orders/AA_Overview_of_Standalone_Orders\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Standalone Orders&lt;/a&gt; feature is enabled.  | [optional] 
**is_adding_subset_charges** | **bool** | Specifies whether to add subset charges to the subscription.  **Note:** This field is available when the EnableAddingSubsetCharges permission is enabled.  | [optional] 

## Example

```python
from zuora_sdk.models.create_order_rate_plan_override import CreateOrderRatePlanOverride

# TODO update the JSON string below
json = "{}"
# create an instance of CreateOrderRatePlanOverride from a JSON string
create_order_rate_plan_override_instance = CreateOrderRatePlanOverride.from_json(json)
# print the JSON string representation of the object
print(CreateOrderRatePlanOverride.to_json())

# convert the object into a dict
create_order_rate_plan_override_dict = create_order_rate_plan_override_instance.to_dict()
# create an instance of CreateOrderRatePlanOverride from a dict
create_order_rate_plan_override_from_dict = CreateOrderRatePlanOverride.from_dict(create_order_rate_plan_override_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


