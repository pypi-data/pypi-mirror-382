# ChargeTier


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ending_unit** | **float** | Limit on the number of units for which the tier is effective.  | [optional] 
**price** | **float** | Price or per-unit price of the tier, depending on the value of the &#x60;priceFormat&#x60; field.  | 
**price_format** | [**PriceFormat**](PriceFormat.md) |  | 
**starting_unit** | **float** | Number of units at which the tier becomes effective.  | 
**tier** | **int** | Index of the tier in the charge.  | 
**original_list_price** | **float** | The original list price is the price of a product or service at which it is listed for sale by a manufacturer or retailer.  | [optional] 

## Example

```python
from zuora_sdk.models.charge_tier import ChargeTier

# TODO update the JSON string below
json = "{}"
# create an instance of ChargeTier from a JSON string
charge_tier_instance = ChargeTier.from_json(json)
# print the JSON string representation of the object
print(ChargeTier.to_json())

# convert the object into a dict
charge_tier_dict = charge_tier_instance.to_dict()
# create an instance of ChargeTier from a dict
charge_tier_from_dict = ChargeTier.from_dict(charge_tier_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


