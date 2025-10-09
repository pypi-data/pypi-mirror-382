# RatePlanChangeLog

Represents the order information that will be returned in the GET call.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**rate_plan_number** | **str** | Rate plan name. | [optional] 
**rate_plan_charges** | [**List[RatePlanChargeChangeLog]**](RatePlanChargeChangeLog.md) | Represents the charges in this rate plan. | [optional] 
**fields** | [**List[ChangeLogField]**](ChangeLogField.md) | Represents the fields which the value is changed for the rate plan. | [optional] 

## Example

```python
from zuora_sdk.models.rate_plan_change_log import RatePlanChangeLog

# TODO update the JSON string below
json = "{}"
# create an instance of RatePlanChangeLog from a JSON string
rate_plan_change_log_instance = RatePlanChangeLog.from_json(json)
# print the JSON string representation of the object
print(RatePlanChangeLog.to_json())

# convert the object into a dict
rate_plan_change_log_dict = rate_plan_change_log_instance.to_dict()
# create an instance of RatePlanChangeLog from a dict
rate_plan_change_log_from_dict = RatePlanChangeLog.from_dict(rate_plan_change_log_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


