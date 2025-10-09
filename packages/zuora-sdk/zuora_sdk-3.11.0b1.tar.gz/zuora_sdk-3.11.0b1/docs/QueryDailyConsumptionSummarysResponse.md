# QueryDailyConsumptionSummarysResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedDailyConsumptionSummary]**](ExpandedDailyConsumptionSummary.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_daily_consumption_summarys_response import QueryDailyConsumptionSummarysResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryDailyConsumptionSummarysResponse from a JSON string
query_daily_consumption_summarys_response_instance = QueryDailyConsumptionSummarysResponse.from_json(json)
# print the JSON string representation of the object
print(QueryDailyConsumptionSummarysResponse.to_json())

# convert the object into a dict
query_daily_consumption_summarys_response_dict = query_daily_consumption_summarys_response_instance.to_dict()
# create an instance of QueryDailyConsumptionSummarysResponse from a dict
query_daily_consumption_summarys_response_from_dict = QueryDailyConsumptionSummarysResponse.from_dict(query_daily_consumption_summarys_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


