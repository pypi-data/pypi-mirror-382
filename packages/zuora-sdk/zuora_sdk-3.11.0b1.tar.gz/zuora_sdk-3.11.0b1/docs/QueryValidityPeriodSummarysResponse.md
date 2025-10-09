# QueryValidityPeriodSummarysResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedValidityPeriodSummary]**](ExpandedValidityPeriodSummary.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_validity_period_summarys_response import QueryValidityPeriodSummarysResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryValidityPeriodSummarysResponse from a JSON string
query_validity_period_summarys_response_instance = QueryValidityPeriodSummarysResponse.from_json(json)
# print the JSON string representation of the object
print(QueryValidityPeriodSummarysResponse.to_json())

# convert the object into a dict
query_validity_period_summarys_response_dict = query_validity_period_summarys_response_instance.to_dict()
# create an instance of QueryValidityPeriodSummarysResponse from a dict
query_validity_period_summarys_response_from_dict = QueryValidityPeriodSummarysResponse.from_dict(query_validity_period_summarys_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


