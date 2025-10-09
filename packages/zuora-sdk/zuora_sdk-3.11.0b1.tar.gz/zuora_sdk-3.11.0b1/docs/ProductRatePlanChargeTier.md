# ProductRatePlanChargeTier


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**currency** | **str** | The code corresponding to the currency for the tier&#39;s price.  | [optional] 
**discount_amount** | **float** | The specific amount for a fixed discount. Required if the charge model of the product rate plan charge is &#x60;Discount-Fixed Amount&#x60;.  | [optional] 
**discount_percentage** | **float** | The percentage of discount for a percentage discount. Required if the charge model of the product rate plan charge is &#x60;Discount-Percentage&#x60;.  | [optional] 
**ending_unit** | **float** | The end number of a range of units for the tier. Required if the charge model of the product rate plan charge is &#x60;Tiered Pricing&#x60; or &#x60;Tiered with Overage Pricing&#x60;.  | [optional] 
**is_overage_price** | **bool** | Indicates if the price is an overage price, which is the price when usage surpasses the last defined tier.  | [optional] 
**price** | **float** | The price of the tier if the charge is a flat fee, or the price of each unit in the tier if the charge model is tiered pricing.  | [optional] 
**price_format** | [**PriceFormatProductRatePlanChargeTier**](PriceFormatProductRatePlanChargeTier.md) |  | [optional] 
**starting_unit** | **float** | The starting number of a range of units for the tier. Required if the charge model of the product rate plan charge is &#x60;Tiered Pricing&#x60; or &#x60;Tiered with Overage Pricing&#x60;.  | [optional] 

## Example

```python
from zuora_sdk.models.product_rate_plan_charge_tier import ProductRatePlanChargeTier

# TODO update the JSON string below
json = "{}"
# create an instance of ProductRatePlanChargeTier from a JSON string
product_rate_plan_charge_tier_instance = ProductRatePlanChargeTier.from_json(json)
# print the JSON string representation of the object
print(ProductRatePlanChargeTier.to_json())

# convert the object into a dict
product_rate_plan_charge_tier_dict = product_rate_plan_charge_tier_instance.to_dict()
# create an instance of ProductRatePlanChargeTier from a dict
product_rate_plan_charge_tier_from_dict = ProductRatePlanChargeTier.from_dict(product_rate_plan_charge_tier_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


