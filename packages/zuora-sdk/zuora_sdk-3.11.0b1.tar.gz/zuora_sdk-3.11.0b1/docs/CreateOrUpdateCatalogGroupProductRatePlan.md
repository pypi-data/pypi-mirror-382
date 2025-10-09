# CreateOrUpdateCatalogGroupProductRatePlan


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**grade** | **float** | The grade that is assigned for the product rate plan. The value of this field must be a positive integer. The greater the value, the higher the grade.   A product rate plan to be added to a Grading catalog group must have one grade. You can specify a grade for a product rate plan in this request or update the product rate plan individually. | [optional] 
**id** | **str** | The unique ID of the product rate plan.  | [optional] 

## Example

```python
from zuora_sdk.models.create_or_update_catalog_group_product_rate_plan import CreateOrUpdateCatalogGroupProductRatePlan

# TODO update the JSON string below
json = "{}"
# create an instance of CreateOrUpdateCatalogGroupProductRatePlan from a JSON string
create_or_update_catalog_group_product_rate_plan_instance = CreateOrUpdateCatalogGroupProductRatePlan.from_json(json)
# print the JSON string representation of the object
print(CreateOrUpdateCatalogGroupProductRatePlan.to_json())

# convert the object into a dict
create_or_update_catalog_group_product_rate_plan_dict = create_or_update_catalog_group_product_rate_plan_instance.to_dict()
# create an instance of CreateOrUpdateCatalogGroupProductRatePlan from a dict
create_or_update_catalog_group_product_rate_plan_from_dict = CreateOrUpdateCatalogGroupProductRatePlan.from_dict(create_or_update_catalog_group_product_rate_plan_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


