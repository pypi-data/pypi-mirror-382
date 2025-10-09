# QuerySummaryStatementsResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedSummaryStatement]**](ExpandedSummaryStatement.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_summary_statements_response import QuerySummaryStatementsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QuerySummaryStatementsResponse from a JSON string
query_summary_statements_response_instance = QuerySummaryStatementsResponse.from_json(json)
# print the JSON string representation of the object
print(QuerySummaryStatementsResponse.to_json())

# convert the object into a dict
query_summary_statements_response_dict = query_summary_statements_response_instance.to_dict()
# create an instance of QuerySummaryStatementsResponse from a dict
query_summary_statements_response_from_dict = QuerySummaryStatementsResponse.from_dict(query_summary_statements_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


