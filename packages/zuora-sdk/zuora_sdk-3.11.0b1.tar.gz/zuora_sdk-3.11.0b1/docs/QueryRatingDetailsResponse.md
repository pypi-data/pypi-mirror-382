# QueryRatingDetailsResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedRatingDetail]**](ExpandedRatingDetail.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_rating_details_response import QueryRatingDetailsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryRatingDetailsResponse from a JSON string
query_rating_details_response_instance = QueryRatingDetailsResponse.from_json(json)
# print the JSON string representation of the object
print(QueryRatingDetailsResponse.to_json())

# convert the object into a dict
query_rating_details_response_dict = query_rating_details_response_instance.to_dict()
# create an instance of QueryRatingDetailsResponse from a dict
query_rating_details_response_from_dict = QueryRatingDetailsResponse.from_dict(query_rating_details_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


