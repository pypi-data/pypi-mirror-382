# ProductRatePlanChargeTierData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**product_rate_plan_charge_tier** | [**List[ProductRatePlanChargeTier]**](ProductRatePlanChargeTier.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.product_rate_plan_charge_tier_data import ProductRatePlanChargeTierData

# TODO update the JSON string below
json = "{}"
# create an instance of ProductRatePlanChargeTierData from a JSON string
product_rate_plan_charge_tier_data_instance = ProductRatePlanChargeTierData.from_json(json)
# print the JSON string representation of the object
print(ProductRatePlanChargeTierData.to_json())

# convert the object into a dict
product_rate_plan_charge_tier_data_dict = product_rate_plan_charge_tier_data_instance.to_dict()
# create an instance of ProductRatePlanChargeTierData from a dict
product_rate_plan_charge_tier_data_from_dict = ProductRatePlanChargeTierData.from_dict(product_rate_plan_charge_tier_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


