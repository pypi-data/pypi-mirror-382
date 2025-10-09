# CreateSubscriptionRatePlan


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**charge_overrides** | [**List[CreateSubscriptionComponent]**](CreateSubscriptionComponent.md) | This optional container is used to override the quantity of one or more product rate plan charges for this subscription.  | [optional] 
**external_catalog_plan_id** | **str** | An external ID of the product rate plan to be added. You can use this field to specify a product rate plan that is imported from an external system. The value of the &#x60;externalCatalogPlanId&#x60; field must match one of the values that are predefined in the &#x60;externallyManagedPlanIds&#x60; field on a product rate plan.  **Note:** If both &#x60;externalCatalogPlanId&#x60; and &#x60;productRatePlanId&#x60; are provided. They must point to the same product rate plan. Otherwise, the request would fail.  | [optional] 
**external_id_source_system** | **str** | The ID of the external source system. You can use this field and &#x60;externalCatalogPlanId&#x60; to specify a product rate plan that is imported from an external system.  **Note:** If both &#x60;externalCatalogPlanId&#x60;, &#x60;externalIdSourceSystem&#x60; and &#x60;productRatePlanId&#x60; are provided. They must point to the same product rate plan. Otherwise, the request would fail.  | [optional] 
**externally_managed_plan_id** | **str** | Indicates the unique identifier for the rate plan purchased on a third-party store. This field is used to represent a subscription rate plan created through third-party stores.  | [optional] 
**product_rate_plan_id** | **str** | ID of a product rate plan for this subscription.  | [optional] 
**product_rate_plan_number** | **str** | Number of a product rate plan for this subscription.  | [optional] 

## Example

```python
from zuora_sdk.models.create_subscription_rate_plan import CreateSubscriptionRatePlan

# TODO update the JSON string below
json = "{}"
# create an instance of CreateSubscriptionRatePlan from a JSON string
create_subscription_rate_plan_instance = CreateSubscriptionRatePlan.from_json(json)
# print the JSON string representation of the object
print(CreateSubscriptionRatePlan.to_json())

# convert the object into a dict
create_subscription_rate_plan_dict = create_subscription_rate_plan_instance.to_dict()
# create an instance of CreateSubscriptionRatePlan from a dict
create_subscription_rate_plan_from_dict = CreateSubscriptionRatePlan.from_dict(create_subscription_rate_plan_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


