# InvoiceScheduleResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**account_id** | **str** | The ID of the customer account that the invoice schedule belongs to.  | [optional] 
**actual_amount** | **decimal.Decimal** | The actual amount that needs to be billed during the processing of the invoice schedule.  By default, the actual amount is the same as the total amount. Even if order changes occur like Remove Product or Cancel Subscription, the value of the &#x60;totalAmount&#x60; field keeps unchanged. The value of the &#x60;actualAmount&#x60; field reflects the actual amount to be billed.  | [optional] 
**additional_subscriptions_to_bill** | **List[str]** | A list of the numbers of the subscriptions that need to be billed together with the invoice schedule.   One invoice schedule can have at most 600 additional subscriptions.  | [optional] 
**billed_amount** | **decimal.Decimal** | The amount that has been billed during the processing of the invoice schedule.  | [optional] 
**id** | **str** | The unique ID of the invoice schedule.  | [optional] 
**invoice_separately** | **bool** | Whether the invoice items created from the invoice schedule appears on a separate invoice when Zuora generates invoices.  | [optional] 
**next_run_date** | **date** | The run date of the next execution of invoice schedule. By default, the next run date is the same as run date of next pending invoice schedule item. It can be overwritten with a different date other than the default value. When the invoice schedule has completed the execution, the next run date is null.  | [optional] 
**notes** | **str** | Comments on the invoice schedule.  | [optional] 
**number** | **str** | The sequence number of the invoice schedule.  | [optional] 
**orders** | **List[str]** | A list of the IDs or numbers of the orders associated with the invoice schedule. One invoice schedule can be associated with at most 10 orders.  | [optional] 
**schedule_items** | [**List[InvoiceScheduleItem]**](InvoiceScheduleItem.md) | Container for schedule items. One invoice schedule can have at most 50 invoice schedule items.  | [optional] 
**specific_subscriptions** | [**List[InvoiceScheduleSubscription]**](InvoiceScheduleSubscription.md) | A list of the numbers of specific subscriptions associated with the invoice schedule.  | [optional] 
**status** | [**InvoiceScheduleStatus**](InvoiceScheduleStatus.md) |  | [optional] 
**total_amount** | **decimal.Decimal** | The total amount that needs to be billed during the processing of the invoice schedule.   The value of this field keeps unchanged once invoice schedule items are created.  | [optional] 
**unbilled_amount** | **decimal.Decimal** | The amount that is waiting to be billed during the processing of the invoice schedule.  | [optional] 

## Example

```python
from zuora_sdk.models.invoice_schedule_response import InvoiceScheduleResponse

# TODO update the JSON string below
json = "{}"
# create an instance of InvoiceScheduleResponse from a JSON string
invoice_schedule_response_instance = InvoiceScheduleResponse.from_json(json)
# print the JSON string representation of the object
print(InvoiceScheduleResponse.to_json())

# convert the object into a dict
invoice_schedule_response_dict = invoice_schedule_response_instance.to_dict()
# create an instance of InvoiceScheduleResponse from a dict
invoice_schedule_response_from_dict = InvoiceScheduleResponse.from_dict(invoice_schedule_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


