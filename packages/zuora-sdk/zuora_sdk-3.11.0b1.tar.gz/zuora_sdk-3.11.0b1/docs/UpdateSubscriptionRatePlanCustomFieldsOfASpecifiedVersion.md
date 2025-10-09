# UpdateSubscriptionRatePlanCustomFieldsOfASpecifiedVersion


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**charges** | [**List[UpdateSubscriptionChargeCustomFieldsOfASpecifiedVersion]**](UpdateSubscriptionChargeCustomFieldsOfASpecifiedVersion.md) |  | [optional] 
**custom_fields** | **Dict[str, object]** | Container for custom fields of a Rate Plan object.  | [optional] 
**rate_plan_id** | **str** | The rate plan id in any version of the subscription. This will be linked to the only one rate plan in the current version. | 

## Example

```python
from zuora_sdk.models.update_subscription_rate_plan_custom_fields_of_a_specified_version import UpdateSubscriptionRatePlanCustomFieldsOfASpecifiedVersion

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateSubscriptionRatePlanCustomFieldsOfASpecifiedVersion from a JSON string
update_subscription_rate_plan_custom_fields_of_a_specified_version_instance = UpdateSubscriptionRatePlanCustomFieldsOfASpecifiedVersion.from_json(json)
# print the JSON string representation of the object
print(UpdateSubscriptionRatePlanCustomFieldsOfASpecifiedVersion.to_json())

# convert the object into a dict
update_subscription_rate_plan_custom_fields_of_a_specified_version_dict = update_subscription_rate_plan_custom_fields_of_a_specified_version_instance.to_dict()
# create an instance of UpdateSubscriptionRatePlanCustomFieldsOfASpecifiedVersion from a dict
update_subscription_rate_plan_custom_fields_of_a_specified_version_from_dict = UpdateSubscriptionRatePlanCustomFieldsOfASpecifiedVersion.from_dict(update_subscription_rate_plan_custom_fields_of_a_specified_version_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


