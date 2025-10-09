# RatePlan


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_fields** | **Dict[str, object]** | Container for custom fields.  | [optional] 
**product_rate_plan_id** | **str** | Internal identifier of the product rate plan that the rate plan is based on. | [optional] 

## Example

```python
from zuora_sdk.models.rate_plan import RatePlan

# TODO update the JSON string below
json = "{}"
# create an instance of RatePlan from a JSON string
rate_plan_instance = RatePlan.from_json(json)
# print the JSON string representation of the object
print(RatePlan.to_json())

# convert the object into a dict
rate_plan_dict = rate_plan_instance.to_dict()
# create an instance of RatePlan from a dict
rate_plan_from_dict = RatePlan.from_dict(rate_plan_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


