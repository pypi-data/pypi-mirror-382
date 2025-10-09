# CreateOrderRatePlanFeatureOverride

Information about feature in rate plan. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_fields** | **Dict[str, object]** | A container for custom fields of the feature.  | [optional] 
**description** | **str** | A description of the feature. | [optional] 
**feature_id** | **str** | Internal identifier of the feature in the product catalog.  | 

## Example

```python
from zuora_sdk.models.create_order_rate_plan_feature_override import CreateOrderRatePlanFeatureOverride

# TODO update the JSON string below
json = "{}"
# create an instance of CreateOrderRatePlanFeatureOverride from a JSON string
create_order_rate_plan_feature_override_instance = CreateOrderRatePlanFeatureOverride.from_json(json)
# print the JSON string representation of the object
print(CreateOrderRatePlanFeatureOverride.to_json())

# convert the object into a dict
create_order_rate_plan_feature_override_dict = create_order_rate_plan_feature_override_instance.to_dict()
# create an instance of CreateOrderRatePlanFeatureOverride from a dict
create_order_rate_plan_feature_override_from_dict = CreateOrderRatePlanFeatureOverride.from_dict(create_order_rate_plan_feature_override_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


