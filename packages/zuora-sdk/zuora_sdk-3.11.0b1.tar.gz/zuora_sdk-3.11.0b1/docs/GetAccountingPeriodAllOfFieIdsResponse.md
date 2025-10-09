# GetAccountingPeriodAllOfFieIdsResponse

File IDs of the reports available for the accounting period. You can retrieve the reports by specifying the file ID in a [Get Files](https://www.zuora.com/developer/api-references/api/operation/Get_Files) REST API call.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**accounts_receivable_account_aging_detail_export_file_id** | **str** | File ID of the Accounts Receivable Aging Account Detail report.  | [optional] 
**accounts_receivable_invoice_aging_detail_export_file_id** | **str** | File ID of the Accounts Receivable Aging Invoice Detail report.  | [optional] 
**accounts_receivable_debit_memo_aging_detail_export_file_id** | **str** | File ID of the Accounts Receivable Aging Debit Memo Detail report.  | [optional] 
**ar_roll_forward_detail_export_file_id** | **str** | File ID of the Accounts Receivable Detail report.  | [optional] 
**fx_realized_gain_and_loss_detail_export_file_id** | **str** | File ID of the Realized Gain and Loss Detail report.  Returned only if you have Foreign Currency Conversion enabled.  | [optional] 
**fx_unrealized_gain_and_loss_detail_export_file_id** | **str** | File ID of the Unrealized Gain and Loss Detail report.  Returned only if you have Foreign Currency Conversion enabled  | [optional] 
**revenue_detail_csv_file_id** | **str** | File ID of the Revenue Detail report in CSV format.  | [optional] 
**revenue_detail_excel_file_id** | **str** | File ID of the Revenue Detail report in XLSX format.  | [optional] 
**unprocessed_charges_file_id** | **str** | File ID of a report containing all unprocessed charges for the accounting period. | [optional] 

## Example

```python
from zuora_sdk.models.get_accounting_period_all_of_fie_ids_response import GetAccountingPeriodAllOfFieIdsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetAccountingPeriodAllOfFieIdsResponse from a JSON string
get_accounting_period_all_of_fie_ids_response_instance = GetAccountingPeriodAllOfFieIdsResponse.from_json(json)
# print the JSON string representation of the object
print(GetAccountingPeriodAllOfFieIdsResponse.to_json())

# convert the object into a dict
get_accounting_period_all_of_fie_ids_response_dict = get_accounting_period_all_of_fie_ids_response_instance.to_dict()
# create an instance of GetAccountingPeriodAllOfFieIdsResponse from a dict
get_accounting_period_all_of_fie_ids_response_from_dict = GetAccountingPeriodAllOfFieIdsResponse.from_dict(get_accounting_period_all_of_fie_ids_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


