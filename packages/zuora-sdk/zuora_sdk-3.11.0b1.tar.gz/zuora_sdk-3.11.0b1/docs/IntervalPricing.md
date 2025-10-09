# IntervalPricing


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sequence** | **int** |  | [optional] 
**type** | **str** |  | [optional] 
**duration** | **int** |  | [optional] 
**price** | **float** |  | [optional] 
**subscription_charge_interval_price_tiers** | [**IntervalPricingTier**](IntervalPricingTier.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.interval_pricing import IntervalPricing

# TODO update the JSON string below
json = "{}"
# create an instance of IntervalPricing from a JSON string
interval_pricing_instance = IntervalPricing.from_json(json)
# print the JSON string representation of the object
print(IntervalPricing.to_json())

# convert the object into a dict
interval_pricing_dict = interval_pricing_instance.to_dict()
# create an instance of IntervalPricing from a dict
interval_pricing_from_dict = IntervalPricing.from_dict(interval_pricing_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


