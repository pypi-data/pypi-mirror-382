# OverrideDiscountApplyDetail


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**product_rate_plan_id** | **str** | Product Rate Plan Id of the discount apply to.  | 
**product_rate_plan_charge_id** | **str** | Product Rate Plan Charge Id of the discount apply to.  | 

## Example

```python
from zuora_sdk.models.override_discount_apply_detail import OverrideDiscountApplyDetail

# TODO update the JSON string below
json = "{}"
# create an instance of OverrideDiscountApplyDetail from a JSON string
override_discount_apply_detail_instance = OverrideDiscountApplyDetail.from_json(json)
# print the JSON string representation of the object
print(OverrideDiscountApplyDetail.to_json())

# convert the object into a dict
override_discount_apply_detail_dict = override_discount_apply_detail_instance.to_dict()
# create an instance of OverrideDiscountApplyDetail from a dict
override_discount_apply_detail_from_dict = OverrideDiscountApplyDetail.from_dict(override_discount_apply_detail_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


