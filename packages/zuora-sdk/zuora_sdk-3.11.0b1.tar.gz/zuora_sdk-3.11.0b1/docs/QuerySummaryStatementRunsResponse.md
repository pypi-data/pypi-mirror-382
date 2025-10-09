# QuerySummaryStatementRunsResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedSummaryStatementRun]**](ExpandedSummaryStatementRun.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_summary_statement_runs_response import QuerySummaryStatementRunsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QuerySummaryStatementRunsResponse from a JSON string
query_summary_statement_runs_response_instance = QuerySummaryStatementRunsResponse.from_json(json)
# print the JSON string representation of the object
print(QuerySummaryStatementRunsResponse.to_json())

# convert the object into a dict
query_summary_statement_runs_response_dict = query_summary_statement_runs_response_instance.to_dict()
# create an instance of QuerySummaryStatementRunsResponse from a dict
query_summary_statement_runs_response_from_dict = QuerySummaryStatementRunsResponse.from_dict(query_summary_statement_runs_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


