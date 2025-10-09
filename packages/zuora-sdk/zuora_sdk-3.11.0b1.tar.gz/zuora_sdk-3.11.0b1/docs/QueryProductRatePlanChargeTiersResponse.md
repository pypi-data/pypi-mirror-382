# QueryProductRatePlanChargeTiersResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedProductRatePlanChargeTier]**](ExpandedProductRatePlanChargeTier.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_product_rate_plan_charge_tiers_response import QueryProductRatePlanChargeTiersResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryProductRatePlanChargeTiersResponse from a JSON string
query_product_rate_plan_charge_tiers_response_instance = QueryProductRatePlanChargeTiersResponse.from_json(json)
# print the JSON string representation of the object
print(QueryProductRatePlanChargeTiersResponse.to_json())

# convert the object into a dict
query_product_rate_plan_charge_tiers_response_dict = query_product_rate_plan_charge_tiers_response_instance.to_dict()
# create an instance of QueryProductRatePlanChargeTiersResponse from a dict
query_product_rate_plan_charge_tiers_response_from_dict = QueryProductRatePlanChargeTiersResponse.from_dict(query_product_rate_plan_charge_tiers_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


