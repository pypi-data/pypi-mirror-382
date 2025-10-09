# GetProductRatePlansByProductResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next_page** | **str** | URL to retrieve the next page of the response if it exists; otherwise absent.  | [optional] 
**product_rate_plans** | [**List[ProductRatePlan]**](ProductRatePlan.md) | Container for one or more product rate plans.  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 

## Example

```python
from zuora_sdk.models.get_product_rate_plans_by_product_response import GetProductRatePlansByProductResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetProductRatePlansByProductResponse from a JSON string
get_product_rate_plans_by_product_response_instance = GetProductRatePlansByProductResponse.from_json(json)
# print the JSON string representation of the object
print(GetProductRatePlansByProductResponse.to_json())

# convert the object into a dict
get_product_rate_plans_by_product_response_dict = get_product_rate_plans_by_product_response_instance.to_dict()
# create an instance of GetProductRatePlansByProductResponse from a dict
get_product_rate_plans_by_product_response_from_dict = GetProductRatePlansByProductResponse.from_dict(get_product_rate_plans_by_product_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


