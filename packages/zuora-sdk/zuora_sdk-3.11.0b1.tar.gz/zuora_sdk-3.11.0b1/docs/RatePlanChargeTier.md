# RatePlanChargeTier


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tier** | **int** | Unique number of the tier.  | [optional] 
**starting_unit** | **float** | Decimal defining start of tier range.  | [optional] 
**ending_unit** | **float** | Decimal defining end of tier range.  | [optional] 
**price** | **float** | The decimal value of the tiered charge model. If the charge model is not a tiered type then this price field will be null and the &#x60;price&#x60; field directly under the &#x60;productRatePlanCharges&#x60; applies. | [optional] 
**price_format** | **str** | Tier price format. Allowed values: &#x60;flat fee&#x60;, &#x60;per unit&#x60;.  | [optional] 
**original_list_price** | **float** | The original list price is the price of a product or service at which it is listed for sale by a manufacturer or retailer.  | [optional] 

## Example

```python
from zuora_sdk.models.rate_plan_charge_tier import RatePlanChargeTier

# TODO update the JSON string below
json = "{}"
# create an instance of RatePlanChargeTier from a JSON string
rate_plan_charge_tier_instance = RatePlanChargeTier.from_json(json)
# print the JSON string representation of the object
print(RatePlanChargeTier.to_json())

# convert the object into a dict
rate_plan_charge_tier_dict = rate_plan_charge_tier_instance.to_dict()
# create an instance of RatePlanChargeTier from a dict
rate_plan_charge_tier_from_dict = RatePlanChargeTier.from_dict(rate_plan_charge_tier_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


