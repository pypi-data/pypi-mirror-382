# UsageTieredWithOveragePricingUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**price_change_option** | [**PriceChangeOption**](PriceChangeOption.md) |  | [optional] [default to PriceChangeOption.NOCHANGE]
**price_increase_percentage** | **float** | Specifies the percentage by which the price of the charge should change each time the subscription renews. Only applicable if the value of the &#x60;priceChangeOption&#x60; field is &#x60;SpecificPercentageValue&#x60;.  | [optional] 
**overage_price** | **float** |  | [optional] 
**tiers** | [**List[ChargeTier]**](ChargeTier.md) |  | [optional] 
**original_list_price** | **float** | The original list price is the price of a product or service at which it is listed for sale by a manufacturer or retailer.  | [optional] 

## Example

```python
from zuora_sdk.models.usage_tiered_with_overage_pricing_update import UsageTieredWithOveragePricingUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of UsageTieredWithOveragePricingUpdate from a JSON string
usage_tiered_with_overage_pricing_update_instance = UsageTieredWithOveragePricingUpdate.from_json(json)
# print the JSON string representation of the object
print(UsageTieredWithOveragePricingUpdate.to_json())

# convert the object into a dict
usage_tiered_with_overage_pricing_update_dict = usage_tiered_with_overage_pricing_update_instance.to_dict()
# create an instance of UsageTieredWithOveragePricingUpdate from a dict
usage_tiered_with_overage_pricing_update_from_dict = UsageTieredWithOveragePricingUpdate.from_dict(usage_tiered_with_overage_pricing_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


