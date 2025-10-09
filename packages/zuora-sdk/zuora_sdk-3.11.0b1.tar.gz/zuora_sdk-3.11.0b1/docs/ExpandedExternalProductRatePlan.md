# ExpandedExternalProductRatePlan


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**external_product_rate_plan_id** | **str** |  | [optional] 
**external_id_source_system** | **str** |  | [optional] 
**rate_plan_id** | **str** |  | [optional] 
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_external_product_rate_plan import ExpandedExternalProductRatePlan

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedExternalProductRatePlan from a JSON string
expanded_external_product_rate_plan_instance = ExpandedExternalProductRatePlan.from_json(json)
# print the JSON string representation of the object
print(ExpandedExternalProductRatePlan.to_json())

# convert the object into a dict
expanded_external_product_rate_plan_dict = expanded_external_product_rate_plan_instance.to_dict()
# create an instance of ExpandedExternalProductRatePlan from a dict
expanded_external_product_rate_plan_from_dict = ExpandedExternalProductRatePlan.from_dict(expanded_external_product_rate_plan_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


