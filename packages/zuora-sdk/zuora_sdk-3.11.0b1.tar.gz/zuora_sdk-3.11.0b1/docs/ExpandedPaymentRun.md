# ExpandedPaymentRun


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**end_date** | **str** |  | [optional] 
**executed_date** | **str** |  | [optional] 
**number_of_credit_balance_adjustments** | **int** |  | [optional] 
**number_of_errors** | **int** |  | [optional] 
**number_of_invoices** | **int** |  | [optional] 
**number_of_payments** | **int** |  | [optional] 
**number_of_unprocessed** | **int** |  | [optional] 
**payment_run_number** | **str** |  | [optional] 
**status** | **str** |  | [optional] 
**target_date** | **date** |  | [optional] 
**apply_credit_balance** | **bool** |  | [optional] 
**consolidated_payment** | **bool** |  | [optional] 
**process_payment_with_closed_pm** | **bool** |  | [optional] 
**collect_payment** | **bool** |  | [optional] 
**auto_apply_credit_memo** | **bool** |  | [optional] 
**auto_apply_unapplied_payment** | **bool** |  | [optional] 
**number_of_credit_memos** | **int** |  | [optional] 
**number_of_debit_memos** | **int** |  | [optional] 
**number_of_debit_memos_unprocessed** | **int** |  | [optional] 
**numberof_unapplied_payments** | **int** |  | [optional] 
**total_execution_time** | **int** |  | [optional] 
**error_message** | **str** |  | [optional] 
**run_date** | **date** |  | [optional] 
**next_run_on** | **date** |  | [optional] 
**repeat_type** | **str** |  | [optional] 
**repeat_from** | **str** |  | [optional] 
**repeat_to** | **str** |  | [optional] 
**run_time** | **int** |  | [optional] 
**time_zone** | **str** |  | [optional] 
**monthly_on_day** | **str** |  | [optional] 
**weekly_on_day** | **str** |  | [optional] 
**account_id** | **str** |  | [optional] 
**batch** | **str** |  | [optional] 
**billing_cycle_day** | **str** |  | [optional] 
**currency** | **str** |  | [optional] 
**payment_gateway_id** | **str** |  | [optional] 
**billing_run_id** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_payment_run import ExpandedPaymentRun

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedPaymentRun from a JSON string
expanded_payment_run_instance = ExpandedPaymentRun.from_json(json)
# print the JSON string representation of the object
print(ExpandedPaymentRun.to_json())

# convert the object into a dict
expanded_payment_run_dict = expanded_payment_run_instance.to_dict()
# create an instance of ExpandedPaymentRun from a dict
expanded_payment_run_from_dict = ExpandedPaymentRun.from_dict(expanded_payment_run_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


