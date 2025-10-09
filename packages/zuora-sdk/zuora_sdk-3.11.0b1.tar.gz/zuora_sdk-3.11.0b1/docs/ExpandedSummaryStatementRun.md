# ExpandedSummaryStatementRun


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**run_type** | **str** |  | [optional] 
**target_account_category** | **str** |  | [optional] 
**statement_run_number** | **str** |  | [optional] 
**account_id** | **str** |  | [optional] 
**batch_name** | **str** |  | [optional] 
**bill_cycle_day** | **str** |  | [optional] 
**date_range_type** | **str** |  | [optional] 
**start_date** | **date** |  | [optional] 
**end_date** | **date** |  | [optional] 
**auto_email_enabled** | **bool** |  | [optional] 
**description** | **str** |  | [optional] 
**status** | **str** |  | [optional] 
**number_of_accounts** | **int** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_summary_statement_run import ExpandedSummaryStatementRun

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedSummaryStatementRun from a JSON string
expanded_summary_statement_run_instance = ExpandedSummaryStatementRun.from_json(json)
# print the JSON string representation of the object
print(ExpandedSummaryStatementRun.to_json())

# convert the object into a dict
expanded_summary_statement_run_dict = expanded_summary_statement_run_instance.to_dict()
# create an instance of ExpandedSummaryStatementRun from a dict
expanded_summary_statement_run_from_dict = ExpandedSummaryStatementRun.from_dict(expanded_summary_statement_run_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


