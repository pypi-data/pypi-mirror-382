# UsageOveragePricingOverride

Pricing information about a usage charge that uses the \"overage\" charge model. In this charge model, the charge has an allowance of free units and a fixed price per additional unit consumed.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**price_change_option** | [**PriceChangeOption**](PriceChangeOption.md) |  | [optional] [default to PriceChangeOption.NOCHANGE]
**price_increase_percentage** | **float** | Specifies the percentage by which the price of the charge should change each time the subscription renews. Only applicable if the value of the &#x60;priceChangeOption&#x60; field is &#x60;SpecificPercentageValue&#x60;.  | [optional] 
**included_units** | **float** | Number of free units that may be consumed.  | [optional] 
**number_of_periods** | **int** | Number of periods that Zuora considers when calculating overage charges with overage smoothing. | [optional] 
**overage_price** | **float** | Price per overage unit consumed.  | [optional] 
**overage_unused_units_credit_option** | **str** | Specifies whether to credit the customer for unused units.   If the value of this field is &#x60;CreditBySpecificRate&#x60;, use the &#x60;unusedUnitsCreditRates&#x60; field to specify the rate at which to credit the customer for unused units. | [optional] 
**unused_units_credit_rates** | **float** | Per-unit rate at which to credit the customer for unused units. Only applicable if the value of the &#x60;overageUnusedUnitsCreditOption&#x60; field is &#x60;CreditBySpecificRate&#x60;. | [optional] 
**original_list_price** | **float** | The original list price is the price of a product or service at which it is listed for sale by a manufacturer or retailer.  | [optional] 

## Example

```python
from zuora_sdk.models.usage_overage_pricing_override import UsageOveragePricingOverride

# TODO update the JSON string below
json = "{}"
# create an instance of UsageOveragePricingOverride from a JSON string
usage_overage_pricing_override_instance = UsageOveragePricingOverride.from_json(json)
# print the JSON string representation of the object
print(UsageOveragePricingOverride.to_json())

# convert the object into a dict
usage_overage_pricing_override_dict = usage_overage_pricing_override_instance.to_dict()
# create an instance of UsageOveragePricingOverride from a dict
usage_overage_pricing_override_from_dict = UsageOveragePricingOverride.from_dict(usage_overage_pricing_override_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


