# CreateOrderProductRatePlanOverride

Information about an order action of type `addProduct`.  

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

## Example

```python
from zuora_sdk.models.create_order_product_rate_plan_override import CreateOrderProductRatePlanOverride

# TODO update the JSON string below
json = "{}"
# create an instance of CreateOrderProductRatePlanOverride from a JSON string
create_order_product_rate_plan_override_instance = CreateOrderProductRatePlanOverride.from_json(json)
# print the JSON string representation of the object
print(CreateOrderProductRatePlanOverride.to_json())

# convert the object into a dict
create_order_product_rate_plan_override_dict = create_order_product_rate_plan_override_instance.to_dict()
# create an instance of CreateOrderProductRatePlanOverride from a dict
create_order_product_rate_plan_override_from_dict = CreateOrderProductRatePlanOverride.from_dict(create_order_product_rate_plan_override_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


