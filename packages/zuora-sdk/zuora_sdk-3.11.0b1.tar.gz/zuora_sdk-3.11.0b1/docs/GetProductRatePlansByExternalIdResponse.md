# GetProductRatePlansByExternalIdResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**product_rate_plans** | [**List[ProductRatePlanWithExternalId]**](ProductRatePlanWithExternalId.md) | Container for one or more product rate plans.  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 

## Example

```python
from zuora_sdk.models.get_product_rate_plans_by_external_id_response import GetProductRatePlansByExternalIdResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetProductRatePlansByExternalIdResponse from a JSON string
get_product_rate_plans_by_external_id_response_instance = GetProductRatePlansByExternalIdResponse.from_json(json)
# print the JSON string representation of the object
print(GetProductRatePlansByExternalIdResponse.to_json())

# convert the object into a dict
get_product_rate_plans_by_external_id_response_dict = get_product_rate_plans_by_external_id_response_instance.to_dict()
# create an instance of GetProductRatePlansByExternalIdResponse from a dict
get_product_rate_plans_by_external_id_response_from_dict = GetProductRatePlansByExternalIdResponse.from_dict(get_product_rate_plans_by_external_id_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


