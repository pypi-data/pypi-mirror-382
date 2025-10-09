# ExpandedRatePlanChargeTier


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**currency** | **str** |  | [optional] 
**discount_amount** | **float** |  | [optional] 
**discount_percentage** | **float** |  | [optional] 
**ending_unit** | **float** |  | [optional] 
**included_units** | **float** |  | [optional] 
**overage_price** | **float** |  | [optional] 
**price** | **float** |  | [optional] 
**price_format** | **str** |  | [optional] 
**starting_unit** | **float** |  | [optional] 
**tier** | **int** |  | [optional] 
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**rate_plan_charge_id** | **str** |  | [optional] 
**rate_plan_charge** | [**ExpandedRatePlanCharge**](ExpandedRatePlanCharge.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_rate_plan_charge_tier import ExpandedRatePlanChargeTier

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedRatePlanChargeTier from a JSON string
expanded_rate_plan_charge_tier_instance = ExpandedRatePlanChargeTier.from_json(json)
# print the JSON string representation of the object
print(ExpandedRatePlanChargeTier.to_json())

# convert the object into a dict
expanded_rate_plan_charge_tier_dict = expanded_rate_plan_charge_tier_instance.to_dict()
# create an instance of ExpandedRatePlanChargeTier from a dict
expanded_rate_plan_charge_tier_from_dict = ExpandedRatePlanChargeTier.from_dict(expanded_rate_plan_charge_tier_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


