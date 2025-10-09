# CatalogGroupProductRatePlan


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** | The description of the product rate plan.  | [optional] 
**effective_end_date** | **str** | The effective end Date of the product rate plan.  | [optional] 
**effective_start_date** | **str** | The effective start date of the product rate plan.  | [optional] 
**grade** | **float** | The grade of the product rate plan.  | [optional] 
**id** | **str** | The ID of the product rate plan.  | [optional] 
**name** | **str** | The name of the product rate plan.  | [optional] 
**status** | [**CatalogGroupStatus**](CatalogGroupStatus.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.catalog_group_product_rate_plan import CatalogGroupProductRatePlan

# TODO update the JSON string below
json = "{}"
# create an instance of CatalogGroupProductRatePlan from a JSON string
catalog_group_product_rate_plan_instance = CatalogGroupProductRatePlan.from_json(json)
# print the JSON string representation of the object
print(CatalogGroupProductRatePlan.to_json())

# convert the object into a dict
catalog_group_product_rate_plan_dict = catalog_group_product_rate_plan_instance.to_dict()
# create an instance of CatalogGroupProductRatePlan from a dict
catalog_group_product_rate_plan_from_dict = CatalogGroupProductRatePlan.from_dict(catalog_group_product_rate_plan_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


