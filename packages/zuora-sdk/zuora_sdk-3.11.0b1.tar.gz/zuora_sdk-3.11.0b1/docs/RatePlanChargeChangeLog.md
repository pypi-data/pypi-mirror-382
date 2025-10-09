# RatePlanChargeChangeLog

Represents the order information that will be returned in the GET call.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**charge_number** | **str** | Charge number. | [optional] 
**rate_plan_charge_id** | **str** | Rate plan charge id. | [optional] 
**effective_start_date** | **str** | Effective start date of this charge. | [optional] 
**effective_end_date** | **str** | Effective end date of this charge. | [optional] 
**fields** | [**List[ChangeLogField]**](ChangeLogField.md) | Represents the fields which the value is changed for this charge. | [optional] 

## Example

```python
from zuora_sdk.models.rate_plan_charge_change_log import RatePlanChargeChangeLog

# TODO update the JSON string below
json = "{}"
# create an instance of RatePlanChargeChangeLog from a JSON string
rate_plan_charge_change_log_instance = RatePlanChargeChangeLog.from_json(json)
# print the JSON string representation of the object
print(RatePlanChargeChangeLog.to_json())

# convert the object into a dict
rate_plan_charge_change_log_dict = rate_plan_charge_change_log_instance.to_dict()
# create an instance of RatePlanChargeChangeLog from a dict
rate_plan_charge_change_log_from_dict = RatePlanChargeChangeLog.from_dict(rate_plan_charge_change_log_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


