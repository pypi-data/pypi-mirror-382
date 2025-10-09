# Tier


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ending_unit** | **float** | End number of a range of units for the tier.  | [optional] 
**price** | **float** | Price of the tier if the charge is a flat fee, or the price of each unit in the tier if the charge model is tiered pricing. | 
**price_format** | **str** | Indicates if pricing is a flat fee or is per unit.  Values:  * &#x60;FlatFee&#x60; * &#x60;PerUnit&#x60;  | [optional] 
**starting_unit** | **float** | Starting number of a range of units for the tier.  | [optional] 
**tier** | **int** | Unique number that identifies the tier that the price applies to.  | 

## Example

```python
from zuora_sdk.models.tier import Tier

# TODO update the JSON string below
json = "{}"
# create an instance of Tier from a JSON string
tier_instance = Tier.from_json(json)
# print the JSON string representation of the object
print(Tier.to_json())

# convert the object into a dict
tier_dict = tier_instance.to_dict()
# create an instance of Tier from a dict
tier_from_dict = Tier.from_dict(tier_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


