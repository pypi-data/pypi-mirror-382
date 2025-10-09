# ExpandedProduct


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**allow_feature_changes** | **bool** |  | [optional] 
**description** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**effective_end_date** | **date** |  | [optional] 
**effective_start_date** | **date** |  | [optional] 
**s_ku** | **str** |  | [optional] 
**id** | **str** |  | [optional] 
**product_number** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**state** | **str** |  | [optional] 
**version** | **str** |  | [optional] 
**version_ordinal** | **int** |  | [optional] 
**category** | **str** |  | [optional] 
**product_rate_plans** | [**List[ExpandedProductRatePlan]**](ExpandedProductRatePlan.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_product import ExpandedProduct

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedProduct from a JSON string
expanded_product_instance = ExpandedProduct.from_json(json)
# print the JSON string representation of the object
print(ExpandedProduct.to_json())

# convert the object into a dict
expanded_product_dict = expanded_product_instance.to_dict()
# create an instance of ExpandedProduct from a dict
expanded_product_from_dict = ExpandedProduct.from_dict(expanded_product_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


