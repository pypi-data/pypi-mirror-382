# RemoveCatalogGroupProductRatePlan


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The unique ID of the product rate plan to be removed from the catalog group. | [optional] 

## Example

```python
from zuora_sdk.models.remove_catalog_group_product_rate_plan import RemoveCatalogGroupProductRatePlan

# TODO update the JSON string below
json = "{}"
# create an instance of RemoveCatalogGroupProductRatePlan from a JSON string
remove_catalog_group_product_rate_plan_instance = RemoveCatalogGroupProductRatePlan.from_json(json)
# print the JSON string representation of the object
print(RemoveCatalogGroupProductRatePlan.to_json())

# convert the object into a dict
remove_catalog_group_product_rate_plan_dict = remove_catalog_group_product_rate_plan_instance.to_dict()
# create an instance of RemoveCatalogGroupProductRatePlan from a dict
remove_catalog_group_product_rate_plan_from_dict = RemoveCatalogGroupProductRatePlan.from_dict(remove_catalog_group_product_rate_plan_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


