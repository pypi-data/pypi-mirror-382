# RatingPropertiesOverride

rating properties information about the charge. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**is_prorate_partial_month** | **bool** | Indicates whether to prorate the charge for the partial month.  | [optional] 
**proration_unit** | [**ChargeProrationRuleProrationUnit**](ChargeProrationRuleProrationUnit.md) |  | [optional] 
**days_in_month** | [**ChargeProrationRuleDaysInMonth**](ChargeProrationRuleDaysInMonth.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.rating_properties_override import RatingPropertiesOverride

# TODO update the JSON string below
json = "{}"
# create an instance of RatingPropertiesOverride from a JSON string
rating_properties_override_instance = RatingPropertiesOverride.from_json(json)
# print the JSON string representation of the object
print(RatingPropertiesOverride.to_json())

# convert the object into a dict
rating_properties_override_dict = rating_properties_override_instance.to_dict()
# create an instance of RatingPropertiesOverride from a dict
rating_properties_override_from_dict = RatingPropertiesOverride.from_dict(rating_properties_override_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


