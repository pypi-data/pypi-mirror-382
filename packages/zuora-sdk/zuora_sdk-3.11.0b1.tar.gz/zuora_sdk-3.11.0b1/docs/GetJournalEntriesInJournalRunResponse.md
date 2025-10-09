# GetJournalEntriesInJournalRunResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**journal_entries** | [**List[GetJournalEntryDetailTypeWithoutSuccess]**](GetJournalEntryDetailTypeWithoutSuccess.md) | Key name that represents the list of journal entries.  | [optional] 
**next_page** | **str** | URL to retrieve the next page of the response if it exists; otherwise absent. | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 

## Example

```python
from zuora_sdk.models.get_journal_entries_in_journal_run_response import GetJournalEntriesInJournalRunResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetJournalEntriesInJournalRunResponse from a JSON string
get_journal_entries_in_journal_run_response_instance = GetJournalEntriesInJournalRunResponse.from_json(json)
# print the JSON string representation of the object
print(GetJournalEntriesInJournalRunResponse.to_json())

# convert the object into a dict
get_journal_entries_in_journal_run_response_dict = get_journal_entries_in_journal_run_response_instance.to_dict()
# create an instance of GetJournalEntriesInJournalRunResponse from a dict
get_journal_entries_in_journal_run_response_from_dict = GetJournalEntriesInJournalRunResponse.from_dict(get_journal_entries_in_journal_run_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


