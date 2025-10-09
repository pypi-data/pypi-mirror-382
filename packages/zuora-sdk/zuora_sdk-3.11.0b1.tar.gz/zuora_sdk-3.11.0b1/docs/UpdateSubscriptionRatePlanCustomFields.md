# UpdateSubscriptionRatePlanCustomFields


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**charges** | [**List[UpdateSubscriptionChargeCustomFields]**](UpdateSubscriptionChargeCustomFields.md) |  | [optional] 
**custom_fields** | **Dict[str, object]** | Container for custom fields of the Rate Plan object. The custom fields of the Rate Plan object are used when rate plans are subscribed. | [optional] 
**rate_plan_id** | **str** | The rate plan id in any version of the subscription. This will be linked to the only one rate plan in the current version. | [optional] 

## Example

```python
from zuora_sdk.models.update_subscription_rate_plan_custom_fields import UpdateSubscriptionRatePlanCustomFields

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateSubscriptionRatePlanCustomFields from a JSON string
update_subscription_rate_plan_custom_fields_instance = UpdateSubscriptionRatePlanCustomFields.from_json(json)
# print the JSON string representation of the object
print(UpdateSubscriptionRatePlanCustomFields.to_json())

# convert the object into a dict
update_subscription_rate_plan_custom_fields_dict = update_subscription_rate_plan_custom_fields_instance.to_dict()
# create an instance of UpdateSubscriptionRatePlanCustomFields from a dict
update_subscription_rate_plan_custom_fields_from_dict = UpdateSubscriptionRatePlanCustomFields.from_dict(update_subscription_rate_plan_custom_fields_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


