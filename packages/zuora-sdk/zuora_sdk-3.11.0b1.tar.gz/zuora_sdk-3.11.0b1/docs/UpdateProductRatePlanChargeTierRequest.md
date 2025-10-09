# UpdateProductRatePlanChargeTierRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**price** | **float** | The price of the tier if the charge is a flat fee, or the price of each unit in the tier if the charge model is tiered pricing. | [optional] 

## Example

```python
from zuora_sdk.models.update_product_rate_plan_charge_tier_request import UpdateProductRatePlanChargeTierRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateProductRatePlanChargeTierRequest from a JSON string
update_product_rate_plan_charge_tier_request_instance = UpdateProductRatePlanChargeTierRequest.from_json(json)
# print the JSON string representation of the object
print(UpdateProductRatePlanChargeTierRequest.to_json())

# convert the object into a dict
update_product_rate_plan_charge_tier_request_dict = update_product_rate_plan_charge_tier_request_instance.to_dict()
# create an instance of UpdateProductRatePlanChargeTierRequest from a dict
update_product_rate_plan_charge_tier_request_from_dict = UpdateProductRatePlanChargeTierRequest.from_dict(update_product_rate_plan_charge_tier_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


