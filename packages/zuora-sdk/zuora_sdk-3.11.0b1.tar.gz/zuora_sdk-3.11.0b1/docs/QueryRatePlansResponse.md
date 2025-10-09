# QueryRatePlansResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedRatePlan]**](ExpandedRatePlan.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_rate_plans_response import QueryRatePlansResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryRatePlansResponse from a JSON string
query_rate_plans_response_instance = QueryRatePlansResponse.from_json(json)
# print the JSON string representation of the object
print(QueryRatePlansResponse.to_json())

# convert the object into a dict
query_rate_plans_response_dict = query_rate_plans_response_instance.to_dict()
# create an instance of QueryRatePlansResponse from a dict
query_rate_plans_response_from_dict = QueryRatePlansResponse.from_dict(query_rate_plans_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


