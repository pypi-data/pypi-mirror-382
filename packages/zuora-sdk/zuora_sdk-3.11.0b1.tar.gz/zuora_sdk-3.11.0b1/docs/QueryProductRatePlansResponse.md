# QueryProductRatePlansResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** |  | [optional] 
**data** | [**List[ExpandedProductRatePlan]**](ExpandedProductRatePlan.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.query_product_rate_plans_response import QueryProductRatePlansResponse

# TODO update the JSON string below
json = "{}"
# create an instance of QueryProductRatePlansResponse from a JSON string
query_product_rate_plans_response_instance = QueryProductRatePlansResponse.from_json(json)
# print the JSON string representation of the object
print(QueryProductRatePlansResponse.to_json())

# convert the object into a dict
query_product_rate_plans_response_dict = query_product_rate_plans_response_instance.to_dict()
# create an instance of QueryProductRatePlansResponse from a dict
query_product_rate_plans_response_from_dict = QueryProductRatePlansResponse.from_dict(query_product_rate_plans_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


