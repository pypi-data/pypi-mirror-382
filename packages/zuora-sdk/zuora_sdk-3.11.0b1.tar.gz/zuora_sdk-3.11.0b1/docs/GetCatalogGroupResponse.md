# GetCatalogGroupResponse


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
from zuora_sdk.models.get_catalog_group_response import GetCatalogGroupResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetCatalogGroupResponse from a JSON string
get_catalog_group_response_instance = GetCatalogGroupResponse.from_json(json)
# print the JSON string representation of the object
print(GetCatalogGroupResponse.to_json())

# convert the object into a dict
get_catalog_group_response_dict = get_catalog_group_response_instance.to_dict()
# create an instance of GetCatalogGroupResponse from a dict
get_catalog_group_response_from_dict = GetCatalogGroupResponse.from_dict(get_catalog_group_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


