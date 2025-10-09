# QueryProcessedUsagesResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedProcessedUsage]**](ExpandedProcessedUsage.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_processed_usages_response import QueryProcessedUsagesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryProcessedUsagesResponse from a JSON string
query_processed_usages_response_instance = QueryProcessedUsagesResponse.from_json(json)
# print the JSON string representation of the object
print(QueryProcessedUsagesResponse.to_json())

# convert the object into a dict
query_processed_usages_response_dict = query_processed_usages_response_instance.to_dict()
# create an instance of QueryProcessedUsagesResponse from a dict
query_processed_usages_response_from_dict = QueryProcessedUsagesResponse.from_dict(query_processed_usages_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


