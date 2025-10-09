# ExpandedSummaryStatement


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**statement_number** | **str** |  | [optional] 
**statement_date** | **date** |  | [optional] 
**start_date** | **date** |  | [optional] 
**end_date** | **date** |  | [optional] 
**account_id** | **str** |  | [optional] 
**file_id** | **str** |  | [optional] 
**status** | **str** |  | [optional] 
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**statement_run_id** | **str** |  | [optional] 
**email_status** | **str** |  | [optional] 
**error_category** | **str** |  | [optional] 
**error_message** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_summary_statement import ExpandedSummaryStatement

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedSummaryStatement from a JSON string
expanded_summary_statement_instance = ExpandedSummaryStatement.from_json(json)
# print the JSON string representation of the object
print(ExpandedSummaryStatement.to_json())

# convert the object into a dict
expanded_summary_statement_dict = expanded_summary_statement_instance.to_dict()
# create an instance of ExpandedSummaryStatement from a dict
expanded_summary_statement_from_dict = ExpandedSummaryStatement.from_dict(expanded_summary_statement_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


