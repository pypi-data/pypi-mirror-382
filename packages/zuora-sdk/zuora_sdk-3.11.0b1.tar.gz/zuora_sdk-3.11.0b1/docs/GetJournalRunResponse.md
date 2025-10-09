# GetJournalRunResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**aggregate_currency** | **bool** |  | [optional] 
**executed_on** | **str** | Date and time the journal run was executed.  | [optional] 
**journal_entry_date** | **date** | Date of the journal entry.  | [optional] 
**number** | **str** | Journal run number.  | [optional] 
**segmentation_rule_name** | **str** | Name of GL segmentation rule used in the journal run.  | [optional] 
**status** | [**JournalRunStatus**](JournalRunStatus.md) |  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 
**target_end_date** | **date** | The target end date of the journal run.  | [optional] 
**target_start_date** | **date** | The target start date of the journal run.  | [optional] 
**total_journal_entry_count** | **int** | Total number of journal entries in the journal run.  | [optional] 
**organization_labels** | [**List[OrganizationLabel]**](OrganizationLabel.md) | Organization Labels.  | [optional] 
**transaction_types** | [**List[GetJournalRunTransactionResponse]**](GetJournalRunTransactionResponse.md) | Transaction types included in the journal run.  | [optional] 

## Example

```python
from zuora_sdk.models.get_journal_run_response import GetJournalRunResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetJournalRunResponse from a JSON string
get_journal_run_response_instance = GetJournalRunResponse.from_json(json)
# print the JSON string representation of the object
print(GetJournalRunResponse.to_json())

# convert the object into a dict
get_journal_run_response_dict = get_journal_run_response_instance.to_dict()
# create an instance of GetJournalRunResponse from a dict
get_journal_run_response_from_dict = GetJournalRunResponse.from_dict(get_journal_run_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


