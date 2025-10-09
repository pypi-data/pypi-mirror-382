# CatalogGroup


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the catalog group.  | [optional] 
**name** | **str** | The name of the catalog group.  | [optional] 
**catalog_group_number** | **str** | The automatically generated number of the catalog group with the CG- perfix. For example, CG-00000001.  | [optional] 
**type** | [**CatalogGroupType**](CatalogGroupType.md) |  | [optional] [default to CatalogGroupType.GRADING]
**description** | **str** | The description of the catalog group.  | [optional] 
**product_rate_plans** | [**List[CatalogGroupProductRatePlan]**](CatalogGroupProductRatePlan.md) | The list of product rate plans in the catalog group.  | [optional] 

## Example

```python
from zuora_sdk.models.catalog_group import CatalogGroup

# TODO update the JSON string below
json = "{}"
# create an instance of CatalogGroup from a JSON string
catalog_group_instance = CatalogGroup.from_json(json)
# print the JSON string representation of the object
print(CatalogGroup.to_json())

# convert the object into a dict
catalog_group_dict = catalog_group_instance.to_dict()
# create an instance of CatalogGroup from a dict
catalog_group_from_dict = CatalogGroup.from_dict(catalog_group_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


