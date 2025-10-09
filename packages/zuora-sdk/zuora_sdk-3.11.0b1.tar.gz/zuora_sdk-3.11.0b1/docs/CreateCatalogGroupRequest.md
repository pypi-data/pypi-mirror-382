# CreateCatalogGroupRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** | The description of the catalog group.  | [optional] 
**name** | **str** | The unique name of the catalog group.  | 
**product_rate_plans** | [**List[CreateOrUpdateCatalogGroupProductRatePlan]**](CreateOrUpdateCatalogGroupProductRatePlan.md) | The list of product rate plans to be added to the catalog group.  | [optional] 
**type** | [**CatalogGroupType**](CatalogGroupType.md) |  | [optional] [default to CatalogGroupType.GRADING]

## Example

```python
from zuora_sdk.models.create_catalog_group_request import CreateCatalogGroupRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateCatalogGroupRequest from a JSON string
create_catalog_group_request_instance = CreateCatalogGroupRequest.from_json(json)
# print the JSON string representation of the object
print(CreateCatalogGroupRequest.to_json())

# convert the object into a dict
create_catalog_group_request_dict = create_catalog_group_request_instance.to_dict()
# create an instance of CreateCatalogGroupRequest from a dict
create_catalog_group_request_from_dict = CreateCatalogGroupRequest.from_dict(create_catalog_group_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


