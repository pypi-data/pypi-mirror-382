# DiscountApplyDetail


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**applied_product_rate_plan_id** | **str** | The ID of the product rate plan that the discount rate plan charge applies to. | [optional] 
**applied_product_rate_plan_charge_id** | **str** | The ID of the product rate plan charge that the discount rate plan charge applies to. | [optional] 
**applied_product_name** | **str** | The name of the product that the discount rate plan charge applies to.  | [optional] 
**applied_product_rate_plan_name** | **str** | The name of the product rate plan that the discount rate plan charge applies to. | [optional] 
**applied_product_rate_plan_charge_name** | **str** | The name of the product rate plan charge that the discount rate plan charge applies to. | [optional] 

## Example

```python
from zuora_sdk.models.discount_apply_detail import DiscountApplyDetail

# TODO update the JSON string below
json = "{}"
# create an instance of DiscountApplyDetail from a JSON string
discount_apply_detail_instance = DiscountApplyDetail.from_json(json)
# print the JSON string representation of the object
print(DiscountApplyDetail.to_json())

# convert the object into a dict
discount_apply_detail_dict = discount_apply_detail_instance.to_dict()
# create an instance of DiscountApplyDetail from a dict
discount_apply_detail_from_dict = DiscountApplyDetail.from_dict(discount_apply_detail_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


