# BillRunSchedule

Container for information about the scheduled bill run. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**repeat_from** | **date** | The start date of the scheduled bill run.  | [optional] 
**repeat_to** | **date** | The end date of of the scheduled bill run.  | [optional] 
**repeat_type** | **str** | The repeat type of the bill run.  | [optional] 
**run_time** | **int** | The scheduled run time (hour) of day.  **Values:** 0 - 23  | [optional] 
**weekly_on_day** | **List[str]** | The repeat day in a week.  | [optional] 
**monthly_on_end_of_month** | **bool** | Whether to schedule monthly bill run on the end of month or the specific day of month. This field is available only when repeatType is set to monthly and repeatFrom is set to the end of month.  For example: - When repeatFrom &#x3D; &#39;2024-04-30&#39; and monthlyOnEndOfMonth &#x3D; true, next bill run will be scheduled on 2024-05-31 - When repeatFrom &#x3D; &#39;2024-04-30&#39; and monthlyOnEndOfMonth &#x3D; false, next bill run will be scheduled on 2024-05-30  | [optional] 

## Example

```python
from zuora_sdk.models.bill_run_schedule import BillRunSchedule

# TODO update the JSON string below
json = "{}"
# create an instance of BillRunSchedule from a JSON string
bill_run_schedule_instance = BillRunSchedule.from_json(json)
# print the JSON string representation of the object
print(BillRunSchedule.to_json())

# convert the object into a dict
bill_run_schedule_dict = bill_run_schedule_instance.to_dict()
# create an instance of BillRunSchedule from a dict
bill_run_schedule_from_dict = BillRunSchedule.from_dict(bill_run_schedule_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


