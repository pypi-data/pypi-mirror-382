# QueryPaymentRunsResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedPaymentRun]**](ExpandedPaymentRun.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_payment_runs_response import QueryPaymentRunsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryPaymentRunsResponse from a JSON string
query_payment_runs_response_instance = QueryPaymentRunsResponse.from_json(json)
# print the JSON string representation of the object
print(QueryPaymentRunsResponse.to_json())

# convert the object into a dict
query_payment_runs_response_dict = query_payment_runs_response_instance.to_dict()
# create an instance of QueryPaymentRunsResponse from a dict
query_payment_runs_response_from_dict = QueryPaymentRunsResponse.from_dict(query_payment_runs_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


