# SubscriptionRatePlan


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Rate plan ID.  | [optional] 
**subscription_rate_plan_number** | **str** |  | [optional] 
**is_from_external_catalog** | **bool** |  | [optional] 
**last_change_type** | **str** | The last amendment on the rate plan.     **Note:** If a subscription is created through an order, this field is only available if multiple orders are created on the subscription.    Possible Values:   * &#x60;Add&#x60;   * &#x60;Update&#x60;   * &#x60;Remove&#x60; | [optional] 
**product_id** | **str** |  | [optional] 
**product_name** | **str** |  | [optional] 
**product_sku** | **str** | The unique SKU for the product. | [optional] 
**product_rate_plan_id** | **str** |  | [optional] 
**product_rate_plan_number** | **str** |  | [optional] 
**rate_plan_name** | **str** | Name of the rate plan. | [optional] 
**subscription_product_features** | [**List[SubscriptionProductFeature]**](SubscriptionProductFeature.md) | Container for one or more features.    Only available when the following settings are enabled:   * The Entitlements feature in your tenant.   * The Enable Feature Specification in Product and Subscriptions setting in Zuora Billing Settings | [optional] 
**externally_managed_plan_id** | **str** | Indicates the unique identifier for the rate plan purchased on a third-party store. This field is used to represent a subscription rate plan created through third-party stores. | [optional] 
**contracted_mrr** | **float** | Monthly recurring revenue of the subscription rate plan exclusive of all the discounts applicable.  | [optional] 
**contracted_net_mrr** | **float** | Monthly recurring revenue of the subscription rate plan inclusive of all the discounts applicable, including the fixed-amount discounts and percentage discounts.  | [optional] 
**as_of_day_gross_mrr** | **float** | Monthly recurring revenue of the subscription rate plan exclusive of any discounts applicable as of specified day.  | [optional] 
**as_of_day_net_mrr** | **float** | Monthly recurring revenue of the subscription rate plan inclusive of all the discounts applicable, including the fixed-amount discounts and percentage discounts as of specified day.  | [optional] 
**rate_plan_charges** | [**List[GetSubscriptionRatePlanChargesWithAllSegments]**](GetSubscriptionRatePlanChargesWithAllSegments.md) | Container for one or more charges. | [optional] 

## Example

```python
from zuora_sdk.models.subscription_rate_plan import SubscriptionRatePlan

# TODO update the JSON string below
json = "{}"
# create an instance of SubscriptionRatePlan from a JSON string
subscription_rate_plan_instance = SubscriptionRatePlan.from_json(json)
# print the JSON string representation of the object
print(SubscriptionRatePlan.to_json())

# convert the object into a dict
subscription_rate_plan_dict = subscription_rate_plan_instance.to_dict()
# create an instance of SubscriptionRatePlan from a dict
subscription_rate_plan_from_dict = SubscriptionRatePlan.from_dict(subscription_rate_plan_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


