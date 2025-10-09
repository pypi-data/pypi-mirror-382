# QueryUsagesResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedUsage]**](ExpandedUsage.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_usages_response import QueryUsagesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryUsagesResponse from a JSON string
query_usages_response_instance = QueryUsagesResponse.from_json(json)
# print the JSON string representation of the object
print(QueryUsagesResponse.to_json())

# convert the object into a dict
query_usages_response_dict = query_usages_response_instance.to_dict()
# create an instance of QueryUsagesResponse from a dict
query_usages_response_from_dict = QueryUsagesResponse.from_dict(query_usages_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


