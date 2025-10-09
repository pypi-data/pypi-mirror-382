# ExpandedProductRatePlan


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**product_id** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**effective_start_date** | **date** |  | [optional] 
**effective_end_date** | **date** |  | [optional] 
**grade** | **int** |  | [optional] 
**product_rate_plan_number** | **str** |  | [optional] 
**state** | **str** |  | [optional] 
**version** | **str** |  | [optional] 
**version_ordinal** | **str** |  | [optional] 
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**product** | [**ExpandedProduct**](ExpandedProduct.md) |  | [optional] 
**product_rate_plan_charges** | [**List[ExpandedProductRatePlanCharge]**](ExpandedProductRatePlanCharge.md) |  | [optional] 
**external_product_rate_plans** | [**List[ExpandedExternalProductRatePlan]**](ExpandedExternalProductRatePlan.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_product_rate_plan import ExpandedProductRatePlan

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedProductRatePlan from a JSON string
expanded_product_rate_plan_instance = ExpandedProductRatePlan.from_json(json)
# print the JSON string representation of the object
print(ExpandedProductRatePlan.to_json())

# convert the object into a dict
expanded_product_rate_plan_dict = expanded_product_rate_plan_instance.to_dict()
# create an instance of ExpandedProductRatePlan from a dict
expanded_product_rate_plan_from_dict = ExpandedProductRatePlan.from_dict(expanded_product_rate_plan_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


