# BillRunResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**id** | **str** | The unique ID of the bill run.  | [optional] 
**name** | **str** | The name of the bill run.  | [optional] 
**bill_run_number** | **str** | The number of the bill run.  | [optional] 
**batches** | **List[str]** | The batch of accounts for this bill run, this field can not exist with &#x60;billRunFilters&#x60; together.   **Values:** &#x60;AllBatches&#x60; or an array of &#x60;Batch&#x60;*n* where *n* is a number between 1 and 50, for example, &#x60;Batch7&#x60;. | [optional] 
**bill_cycle_day** | **str** | The day of the bill cycle, this field is only valid when &#x60;batches&#x60; is specified.   **Values:**   - &#x60;AllBillCycleDays&#x60; or one of numbers 1 - 31 for an ad-hoc bill run  - &#x60;AllBillCycleDays&#x60;, one of numbers 1 - 31, or &#x60;AsRunDay&#x60; for a scheduled bill run | [optional] 
**bill_run_filters** | [**List[BillRunFilter]**](BillRunFilter.md) | The target account or subscriptions for this bill run.  | [optional] 
**charge_type_to_exclude** | [**List[ChargeType]**](ChargeType.md) | The types of the charges to be excluded from the generation of billing documents. | [optional] 
**auto_email** | **bool** | Whether to automatically send emails after Auto-Post is complete.  | [optional] 
**auto_post** | **bool** | Whether to automatically post the bill run after the bill run is created. | [optional] 
**auto_renewal** | **bool** | Whether to automatically renew auto-renew subscriptions that are up for renewal. | [optional] 
**no_email_for_zero_amount_invoice** | **bool** | Whether to suppress emails for invoices with zero total amount generated in this bill run after the bill run is complete. | [optional] 
**schedule** | [**BillRunSchedule**](BillRunSchedule.md) |  | [optional] 
**scheduled_execution_time** | **str** | The scheduled execution time for a bill run.  | [optional] 
**status** | [**BillRunStatus**](BillRunStatus.md) |  | [optional] 
**invoice_date** | **date** | The invoice date for this bill run, only valid for ad-hoc bill runs.  | [optional] 
**invoice_date_offset** | **int** | The offset compared to bill run execution date, only valid for scheduled bill runs. | [optional] 
**invoice_date_month_offset** | **int** | The month offset of invoice date for this bill run based on run date, only valid for monthly scheduled bill runs. invoiceDateOffset and invoiceDateMonthOffset/invoiceDateDayOfMonth are mutually exclusive. invoiceDateMonthOffset and invoiceDateDayOfMonth coexist.  | [optional] 
**invoice_date_day_of_month** | **int** | The day of month of invoice date for this bill run, only valid for monthly scheduled bill runs. The value is between 1 and 31, where 31 &#x3D; end-of-month. invoiceDateOffset and invoiceDateMonthOffset/invoiceDateDayOfMonth are mutually exclusive. invoiceDateMonthOffset and invoiceDateDayOfMonth coexist.  | [optional] 
**target_date** | **date** | The target date for this bill run, only valid for ad-hoc bill runs.  | [optional] 
**target_date_offset** | **int** | The offset compared to bill run execution date, only valid for scheduled bill runs. | [optional] 
**target_date_month_offset** | **int** | The month offset of target date for this bill run based on run date, only valid for monthly scheduled bill runs. targetDateOffset and targetDateMonthOffset/targetDateDayOfMonth are mutually exclusive. targetDateMonthOffset and targetDateDayOfMonth coexist.  | [optional] 
**target_date_day_of_month** | **int** | The day of month of target date for this bill run, only valid for monthly scheduled bill runs. The value is between 1 and 31, where 31 &#x3D; end-of-month. targetDateOffset and targetDateMonthOffset/targetDateDayOfMonth are mutually exclusive. targetDateMonthOffset and targetDateDayOfMonth coexist.  | [optional] 
**include_subscriptions** | **bool** | Whether to bill subscriptions.  | [optional] 
**include_order_line_items** | **bool** | Whether to bill order line items.  | [optional] 
**created_by_id** | **str** | The ID of the user who created the bill run.  | [optional] 
**created_date** | **str** | The date and time when the bill run was created.  | [optional] 
**updated_by_id** | **str** | The ID of the user who last updated the bill run.  | [optional] 
**updated_date** | **str** | The date and time when the bill run was last updated.  | [optional] 

## Example

```python
from zuora_sdk.models.bill_run_response import BillRunResponse

# TODO update the JSON string below
json = "{}"
# create an instance of BillRunResponse from a JSON string
bill_run_response_instance = BillRunResponse.from_json(json)
# print the JSON string representation of the object
print(BillRunResponse.to_json())

# convert the object into a dict
bill_run_response_dict = bill_run_response_instance.to_dict()
# create an instance of BillRunResponse from a dict
bill_run_response_from_dict = BillRunResponse.from_dict(bill_run_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


