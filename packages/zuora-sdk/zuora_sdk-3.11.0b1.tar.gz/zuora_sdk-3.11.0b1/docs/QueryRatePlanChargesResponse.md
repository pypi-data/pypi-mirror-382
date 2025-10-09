# QueryRatePlanChargesResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedRatePlanCharge]**](ExpandedRatePlanCharge.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_rate_plan_charges_response import QueryRatePlanChargesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryRatePlanChargesResponse from a JSON string
query_rate_plan_charges_response_instance = QueryRatePlanChargesResponse.from_json(json)
# print the JSON string representation of the object
print(QueryRatePlanChargesResponse.to_json())

# convert the object into a dict
query_rate_plan_charges_response_dict = query_rate_plan_charges_response_instance.to_dict()
# create an instance of QueryRatePlanChargesResponse from a dict
query_rate_plan_charges_response_from_dict = QueryRatePlanChargesResponse.from_dict(query_rate_plan_charges_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


