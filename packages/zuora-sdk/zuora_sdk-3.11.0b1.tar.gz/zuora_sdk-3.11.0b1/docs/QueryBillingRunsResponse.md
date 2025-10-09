# QueryBillingRunsResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedBillingRun]**](ExpandedBillingRun.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_billing_runs_response import QueryBillingRunsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryBillingRunsResponse from a JSON string
query_billing_runs_response_instance = QueryBillingRunsResponse.from_json(json)
# print the JSON string representation of the object
print(QueryBillingRunsResponse.to_json())

# convert the object into a dict
query_billing_runs_response_dict = query_billing_runs_response_instance.to_dict()
# create an instance of QueryBillingRunsResponse from a dict
query_billing_runs_response_from_dict = QueryBillingRunsResponse.from_dict(query_billing_runs_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


