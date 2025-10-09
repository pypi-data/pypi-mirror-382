# GetCatalogGroupsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**catalog_groups** | [**List[CatalogGroup]**](CatalogGroup.md) | The list of catalog groups that are retrieved..  | [optional] 
**next_page** | **str** | URL to retrieve the next page of the response if it exists; otherwise absent. | [optional] 

## Example

```python
from zuora_sdk.models.get_catalog_groups_response import GetCatalogGroupsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetCatalogGroupsResponse from a JSON string
get_catalog_groups_response_instance = GetCatalogGroupsResponse.from_json(json)
# print the JSON string representation of the object
print(GetCatalogGroupsResponse.to_json())

# convert the object into a dict
get_catalog_groups_response_dict = get_catalog_groups_response_instance.to_dict()
# create an instance of GetCatalogGroupsResponse from a dict
get_catalog_groups_response_from_dict = GetCatalogGroupsResponse.from_dict(get_catalog_groups_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


