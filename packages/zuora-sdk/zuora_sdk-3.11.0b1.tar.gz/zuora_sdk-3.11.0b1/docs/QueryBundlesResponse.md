# QueryBundlesResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedBundle]**](ExpandedBundle.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_bundles_response import QueryBundlesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryBundlesResponse from a JSON string
query_bundles_response_instance = QueryBundlesResponse.from_json(json)
# print the JSON string representation of the object
print(QueryBundlesResponse.to_json())

# convert the object into a dict
query_bundles_response_dict = query_bundles_response_instance.to_dict()
# create an instance of QueryBundlesResponse from a dict
query_bundles_response_from_dict = QueryBundlesResponse.from_dict(query_bundles_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


