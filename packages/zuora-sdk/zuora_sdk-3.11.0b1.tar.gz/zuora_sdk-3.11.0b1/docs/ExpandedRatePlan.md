# ExpandedRatePlan


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**product_id** | **str** |  | [optional] 
**amendment_id** | **str** |  | [optional] 
**amendment_type** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**product_rate_plan_id** | **str** |  | [optional] 
**subscription_id** | **str** |  | [optional] 
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**subscription_owner_id** | **str** |  | [optional] 
**invoice_owner_id** | **str** |  | [optional] 
**externally_managed_plan_id** | **str** |  | [optional] 
**original_rate_plan_id** | **str** |  | [optional] 
**subscription_offer_id** | **str** |  | [optional] 
**subscription_rate_plan_number** | **str** |  | [optional] 
**reverted** | **bool** |  | [optional] 
**pricing_attributes** | **str** |  | [optional] 
**subscription** | [**ExpandedSubscription**](ExpandedSubscription.md) |  | [optional] 
**product_rate_plan** | [**ExpandedProductRatePlan**](ExpandedProductRatePlan.md) |  | [optional] 
**rate_plan_charges** | [**List[ExpandedRatePlanCharge]**](ExpandedRatePlanCharge.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_rate_plan import ExpandedRatePlan

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedRatePlan from a JSON string
expanded_rate_plan_instance = ExpandedRatePlan.from_json(json)
# print the JSON string representation of the object
print(ExpandedRatePlan.to_json())

# convert the object into a dict
expanded_rate_plan_dict = expanded_rate_plan_instance.to_dict()
# create an instance of ExpandedRatePlan from a dict
expanded_rate_plan_from_dict = ExpandedRatePlan.from_dict(expanded_rate_plan_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


