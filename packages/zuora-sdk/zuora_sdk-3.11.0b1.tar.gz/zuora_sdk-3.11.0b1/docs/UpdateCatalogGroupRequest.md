# UpdateCatalogGroupRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**add** | [**List[CreateOrUpdateCatalogGroupProductRatePlan]**](CreateOrUpdateCatalogGroupProductRatePlan.md) | The list of product rate plans to be added to the catalog group.  | [optional] 
**description** | **str** | The description of the catalog group.  | [optional] 
**name** | **str** | The unique name of the catalog group.  | [optional] 
**remove** | **List[List[RemoveCatalogGroupProductRatePlan]]** | The list of product rate plans to be removed from the catalog group.  | [optional] 

## Example

```python
from zuora_sdk.models.update_catalog_group_request import UpdateCatalogGroupRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateCatalogGroupRequest from a JSON string
update_catalog_group_request_instance = UpdateCatalogGroupRequest.from_json(json)
# print the JSON string representation of the object
print(UpdateCatalogGroupRequest.to_json())

# convert the object into a dict
update_catalog_group_request_dict = update_catalog_group_request_instance.to_dict()
# create an instance of UpdateCatalogGroupRequest from a dict
update_catalog_group_request_from_dict = UpdateCatalogGroupRequest.from_dict(update_catalog_group_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


