# DiscountPricingUpdate


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**apply_discount_to** | [**ApplyDiscountTo**](ApplyDiscountTo.md) |  | [optional] 
**discount_level** | [**DiscountLevel**](DiscountLevel.md) |  | [optional] 
**discount_percentage** | **float** | The amount of the discount as a percentage. This field is only used for percentage discounts.  | [optional] 
**price_change_option** | [**PriceChangeOption**](PriceChangeOption.md) |  | [optional] [default to PriceChangeOption.NOCHANGE]

## Example

```python
from zuora_sdk.models.discount_pricing_update import DiscountPricingUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of DiscountPricingUpdate from a JSON string
discount_pricing_update_instance = DiscountPricingUpdate.from_json(json)
# print the JSON string representation of the object
print(DiscountPricingUpdate.to_json())

# convert the object into a dict
discount_pricing_update_dict = discount_pricing_update_instance.to_dict()
# create an instance of DiscountPricingUpdate from a dict
discount_pricing_update_from_dict = DiscountPricingUpdate.from_dict(discount_pricing_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


