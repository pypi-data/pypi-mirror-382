# ExpandedInvoiceSchedule


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**total_amount** | **float** |  | [optional] 
**actual_amount** | **float** |  | [optional] 
**billed_amount** | **float** |  | [optional] 
**unbilled_amount** | **float** |  | [optional] 
**next_run_date** | **date** |  | [optional] 
**number** | **str** |  | [optional] 
**notes** | **str** |  | [optional] 
**account_id** | **str** |  | [optional] 
**status** | **str** |  | [optional] 
**additional_subscriptions_to_bill** | **str** |  | [optional] 
**currency** | **str** |  | [optional] 
**invoice_schedule_items** | [**List[ExpandedInvoiceScheduleItem]**](ExpandedInvoiceScheduleItem.md) |  | [optional] 
**invoice_schedule_bookings** | [**List[ExpandedInvoiceScheduleBooking]**](ExpandedInvoiceScheduleBooking.md) |  | [optional] 
**rate_plan_charges** | [**List[ExpandedRatePlanCharge]**](ExpandedRatePlanCharge.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_invoice_schedule import ExpandedInvoiceSchedule

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedInvoiceSchedule from a JSON string
expanded_invoice_schedule_instance = ExpandedInvoiceSchedule.from_json(json)
# print the JSON string representation of the object
print(ExpandedInvoiceSchedule.to_json())

# convert the object into a dict
expanded_invoice_schedule_dict = expanded_invoice_schedule_instance.to_dict()
# create an instance of ExpandedInvoiceSchedule from a dict
expanded_invoice_schedule_from_dict = ExpandedInvoiceSchedule.from_dict(expanded_invoice_schedule_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


