# QueryRatePlanChargeTiersResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedRatePlanChargeTier]**](ExpandedRatePlanChargeTier.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_rate_plan_charge_tiers_response import QueryRatePlanChargeTiersResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryRatePlanChargeTiersResponse from a JSON string
query_rate_plan_charge_tiers_response_instance = QueryRatePlanChargeTiersResponse.from_json(json)
# print the JSON string representation of the object
print(QueryRatePlanChargeTiersResponse.to_json())

# convert the object into a dict
query_rate_plan_charge_tiers_response_dict = query_rate_plan_charge_tiers_response_instance.to_dict()
# create an instance of QueryRatePlanChargeTiersResponse from a dict
query_rate_plan_charge_tiers_response_from_dict = QueryRatePlanChargeTiersResponse.from_dict(query_rate_plan_charge_tiers_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


