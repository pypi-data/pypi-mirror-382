# OrderActionRemoveProduct

Information about an order action of type `RemoveProduct`.   A rate plan can be removed from a subscription through one order action.  - If you remove a rate plan, specify the following fields:   - `externalCatalogPlanId`   - `ratePlanId`   - `subscriptionRatePlanNumber`   - `productRatePlanNumber`   - `uniqueToken`

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**external_catalog_plan_id** | **str** | An external ID of the rate plan to be removed. You can use this field to specify an existing rate plan in your subscription. The value of the &#x60;externalCatalogPlanId&#x60; field must match one of the values that are predefined in the &#x60;externallyManagedPlanIds&#x60; field on a product rate plan. However, if there are multiple rate plans with the same &#x60;productRatePlanId&#x60; value existing in the subscription, you must use the &#x60;ratePlanId&#x60; field to remove the rate plan. The &#x60;externalCatalogPlanId&#x60; field cannot be used to distinguish multiple rate plans in this case.   **Note:** If both &#x60;externalCatalogPlanId&#x60; and &#x60;ratePlanId&#x60; are provided. They must point to the same product rate plan. Otherwise, the request would fail. | [optional] 
**product_rate_plan_number** | **str** | Number of a product rate plan for this subscription.  | [optional] 
**product_rate_plan_id** | **str** | ID of a product rate plan for this subscription.  | [optional] 
**rate_plan_id** | **str** | ID of the rate plan to remove. This can be the latest version or any history version of ID. | [optional] 
**subscription_rate_plan_number** | **str** | Number of a rate plan for this subscription.  | [optional] 
**unique_token** | **str** | Unique identifier for the rate plan. This identifier enables you to refer to the rate plan before the rate plan has an internal identifier in Zuora. | [optional] 
**custom_fields** | **Dict[str, object]** | Container for custom fields of a Rate Plan object.  | [optional] 
**charge_updates** | [**List[OrderActionRatePlanChargeRemove]**](OrderActionRatePlanChargeRemove.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.order_action_remove_product import OrderActionRemoveProduct

# TODO update the JSON string below
json = "{}"
# create an instance of OrderActionRemoveProduct from a JSON string
order_action_remove_product_instance = OrderActionRemoveProduct.from_json(json)
# print the JSON string representation of the object
print(OrderActionRemoveProduct.to_json())

# convert the object into a dict
order_action_remove_product_dict = order_action_remove_product_instance.to_dict()
# create an instance of OrderActionRemoveProduct from a dict
order_action_remove_product_from_dict = OrderActionRemoveProduct.from_dict(order_action_remove_product_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


