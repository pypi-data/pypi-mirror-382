# UsageVolumePricingUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**price_change_option** | [**PriceChangeOption**](PriceChangeOption.md) |  | [optional] [default to PriceChangeOption.NOCHANGE]
**price_increase_percentage** | **float** | Specifies the percentage by which the price of the charge should change each time the subscription renews. Only applicable if the value of the &#x60;priceChangeOption&#x60; field is &#x60;SpecificPercentageValue&#x60;.  | [optional] 
**tiers** | [**List[ChargeTier]**](ChargeTier.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.usage_volume_pricing_update import UsageVolumePricingUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of UsageVolumePricingUpdate from a JSON string
usage_volume_pricing_update_instance = UsageVolumePricingUpdate.from_json(json)
# print the JSON string representation of the object
print(UsageVolumePricingUpdate.to_json())

# convert the object into a dict
usage_volume_pricing_update_dict = usage_volume_pricing_update_instance.to_dict()
# create an instance of UsageVolumePricingUpdate from a dict
usage_volume_pricing_update_from_dict = UsageVolumePricingUpdate.from_dict(usage_volume_pricing_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


