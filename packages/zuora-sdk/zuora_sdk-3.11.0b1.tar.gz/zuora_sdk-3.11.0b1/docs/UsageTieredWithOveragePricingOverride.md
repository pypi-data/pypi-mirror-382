# UsageTieredWithOveragePricingOverride

Pricing information about a usage charge that uses the \"tiered with overage\" charge model. In this charge model, the charge has cumulative pricing tiers that become effective as units are consumed. The charge also has a fixed price per unit consumed beyond the limit of the final tier.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**price_change_option** | [**PriceChangeOption**](PriceChangeOption.md) |  | [optional] [default to PriceChangeOption.NOCHANGE]
**price_increase_percentage** | **float** | Specifies the percentage by which the price of the charge should change each time the subscription renews. Only applicable if the value of the &#x60;priceChangeOption&#x60; field is &#x60;SpecificPercentageValue&#x60;.  | [optional] 
**number_of_periods** | **int** | Number of periods that Zuora considers when calculating overage charges with overage smoothing. | [optional] 
**overage_price** | **float** | Price per overage unit consumed.  | [optional] 
**overage_unused_units_credit_option** | **str** | Specifies whether to credit the customer for unused units.   If the value of this field is &#x60;CreditBySpecificRate&#x60;, use the &#x60;unusedUnitsCreditRates&#x60; field to specify the rate at which to credit the customer for unused units. | [optional] 
**tiers** | [**List[ChargeTier]**](ChargeTier.md) | List of cumulative pricing tiers in the charge.  | [optional] 
**unused_units_credit_rates** | **float** | Per-unit rate at which to credit the customer for unused units. Only applicable if the value of the &#x60;overageUnusedUnitsCreditOption&#x60; field is &#x60;CreditBySpecificRate&#x60;. | [optional] 
**original_list_price** | **float** | The original list price is the price of a product or service at which it is listed for sale by a manufacturer or retailer.  | [optional] 

## Example

```python
from zuora_sdk.models.usage_tiered_with_overage_pricing_override import UsageTieredWithOveragePricingOverride

# TODO update the JSON string below
json = "{}"
# create an instance of UsageTieredWithOveragePricingOverride from a JSON string
usage_tiered_with_overage_pricing_override_instance = UsageTieredWithOveragePricingOverride.from_json(json)
# print the JSON string representation of the object
print(UsageTieredWithOveragePricingOverride.to_json())

# convert the object into a dict
usage_tiered_with_overage_pricing_override_dict = usage_tiered_with_overage_pricing_override_instance.to_dict()
# create an instance of UsageTieredWithOveragePricingOverride from a dict
usage_tiered_with_overage_pricing_override_from_dict = UsageTieredWithOveragePricingOverride.from_dict(usage_tiered_with_overage_pricing_override_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


