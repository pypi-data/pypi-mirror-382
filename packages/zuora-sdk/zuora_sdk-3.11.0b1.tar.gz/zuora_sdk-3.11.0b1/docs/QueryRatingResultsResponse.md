# QueryRatingResultsResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedRatingResult]**](ExpandedRatingResult.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_rating_results_response import QueryRatingResultsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryRatingResultsResponse from a JSON string
query_rating_results_response_instance = QueryRatingResultsResponse.from_json(json)
# print the JSON string representation of the object
print(QueryRatingResultsResponse.to_json())

# convert the object into a dict
query_rating_results_response_dict = query_rating_results_response_instance.to_dict()
# create an instance of QueryRatingResultsResponse from a dict
query_rating_results_response_from_dict = QueryRatingResultsResponse.from_dict(query_rating_results_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


