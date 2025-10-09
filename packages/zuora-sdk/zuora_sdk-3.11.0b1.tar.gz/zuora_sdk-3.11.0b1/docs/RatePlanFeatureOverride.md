# RatePlanFeatureOverride

Information about feature in rate plan. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_fields** | **Dict[str, object]** | A container for custom fields of the feature.  | [optional] 
**description** | **str** | A description of the feature. | [optional] 
**feature_id** | **str** | Internal identifier of the feature in the product catalog.  | [optional] 
**id** | **str** | Internal identifier of the rate plan feature override.  | [optional] 

## Example

```python
from zuora_sdk.models.rate_plan_feature_override import RatePlanFeatureOverride

# TODO update the JSON string below
json = "{}"
# create an instance of RatePlanFeatureOverride from a JSON string
rate_plan_feature_override_instance = RatePlanFeatureOverride.from_json(json)
# print the JSON string representation of the object
print(RatePlanFeatureOverride.to_json())

# convert the object into a dict
rate_plan_feature_override_dict = rate_plan_feature_override_instance.to_dict()
# create an instance of RatePlanFeatureOverride from a dict
rate_plan_feature_override_from_dict = RatePlanFeatureOverride.from_dict(rate_plan_feature_override_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


