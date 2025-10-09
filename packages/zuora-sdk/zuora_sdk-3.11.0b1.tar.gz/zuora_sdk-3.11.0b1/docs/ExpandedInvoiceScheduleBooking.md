# ExpandedInvoiceScheduleBooking


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**invoice_schedule_id** | **str** |  | [optional] 
**order_id** | **str** |  | [optional] 
**order_number** | **str** |  | [optional] 
**subscription_id** | **str** |  | [optional] 
**subscription_number** | **str** |  | [optional] 
**charge_numbers** | **str** |  | [optional] 
**order** | [**ExpandedOrders**](ExpandedOrders.md) |  | [optional] 
**subscription** | [**ExpandedSubscription**](ExpandedSubscription.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_invoice_schedule_booking import ExpandedInvoiceScheduleBooking

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedInvoiceScheduleBooking from a JSON string
expanded_invoice_schedule_booking_instance = ExpandedInvoiceScheduleBooking.from_json(json)
# print the JSON string representation of the object
print(ExpandedInvoiceScheduleBooking.to_json())

# convert the object into a dict
expanded_invoice_schedule_booking_dict = expanded_invoice_schedule_booking_instance.to_dict()
# create an instance of ExpandedInvoiceScheduleBooking from a dict
expanded_invoice_schedule_booking_from_dict = ExpandedInvoiceScheduleBooking.from_dict(expanded_invoice_schedule_booking_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


