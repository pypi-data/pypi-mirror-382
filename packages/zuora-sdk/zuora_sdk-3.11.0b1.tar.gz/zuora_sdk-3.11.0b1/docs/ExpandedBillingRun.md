# ExpandedBillingRun


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**billing_run_number** | **str** |  | [optional] 
**billing_run_type** | **str** |  | [optional] 
**end_date** | **str** |  | [optional] 
**error_message** | **str** |  | [optional] 
**executed_date** | **str** |  | [optional] 
**invoice_date** | **date** |  | [optional] 
**name** | **str** |  | [optional] 
**number_of_accounts** | **int** |  | [optional] 
**number_of_invoices** | **int** |  | [optional] 
**number_of_credit_memos** | **int** |  | [optional] 
**posted_date** | **str** |  | [optional] 
**start_date** | **str** |  | [optional] 
**status** | **str** |  | [optional] 
**target_date** | **date** |  | [optional] 
**target_type** | **str** |  | [optional] 
**total_time** | **int** |  | [optional] 
**account_id** | **str** |  | [optional] 
**bill_cycle_day** | **str** |  | [optional] 
**batches** | **str** |  | [optional] 
**no_email_for_zero_amount_invoice** | **bool** |  | [optional] 
**auto_post** | **bool** |  | [optional] 
**auto_email** | **bool** |  | [optional] 
**auto_renewal** | **bool** |  | [optional] 
**invoices_emailed** | **bool** |  | [optional] 
**last_email_sent_time** | **str** |  | [optional] 
**target_date_off_set** | **int** |  | [optional] 
**invoice_date_off_set** | **int** |  | [optional] 
**charge_type_to_exclude** | **str** |  | [optional] 
**scheduled_execution_time** | **str** |  | [optional] 
**target_date_month_offset** | **int** |  | [optional] 
**target_date_day_of_month** | **str** |  | [optional] 
**invoice_date_month_offset** | **int** |  | [optional] 
**invoice_date_day_of_month** | **str** |  | [optional] 
**include_subscriptions** | **bool** |  | [optional] 
**include_order_line_items** | **bool** |  | [optional] 
**repeat_type** | **str** |  | [optional] 
**repeat_from** | **str** |  | [optional] 
**repeat_to** | **str** |  | [optional] 
**run_time** | **int** |  | [optional] 
**time_zone** | **str** |  | [optional] 
**monthly_on_day** | **str** |  | [optional] 
**weekly_on_day** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_billing_run import ExpandedBillingRun

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedBillingRun from a JSON string
expanded_billing_run_instance = ExpandedBillingRun.from_json(json)
# print the JSON string representation of the object
print(ExpandedBillingRun.to_json())

# convert the object into a dict
expanded_billing_run_dict = expanded_billing_run_instance.to_dict()
# create an instance of ExpandedBillingRun from a dict
expanded_billing_run_from_dict = ExpandedBillingRun.from_dict(expanded_billing_run_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


