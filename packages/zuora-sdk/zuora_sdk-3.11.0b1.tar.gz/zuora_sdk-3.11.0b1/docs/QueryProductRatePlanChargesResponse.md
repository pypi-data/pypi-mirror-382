# QueryProductRatePlanChargesResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedProductRatePlanCharge]**](ExpandedProductRatePlanCharge.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_product_rate_plan_charges_response import QueryProductRatePlanChargesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryProductRatePlanChargesResponse from a JSON string
query_product_rate_plan_charges_response_instance = QueryProductRatePlanChargesResponse.from_json(json)
# print the JSON string representation of the object
print(QueryProductRatePlanChargesResponse.to_json())

# convert the object into a dict
query_product_rate_plan_charges_response_dict = query_product_rate_plan_charges_response_instance.to_dict()
# create an instance of QueryProductRatePlanChargesResponse from a dict
query_product_rate_plan_charges_response_from_dict = QueryProductRatePlanChargesResponse.from_dict(query_product_rate_plan_charges_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


