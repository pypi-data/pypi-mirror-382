# UpdateBasicSummaryJournalEntryRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**journal_entry_items** | [**List[UpdateJournalEntryItemRequest]**](UpdateJournalEntryItemRequest.md) | Key name that represents the list of journal entry items.  | [optional] 
**notes** | **str** | Additional information about this record.  ***Character limit:*** 2,000  | [optional] 
**transferred_to_accounting** | [**TransferredToAccountingStatus**](TransferredToAccountingStatus.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.update_basic_summary_journal_entry_request import UpdateBasicSummaryJournalEntryRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateBasicSummaryJournalEntryRequest from a JSON string
update_basic_summary_journal_entry_request_instance = UpdateBasicSummaryJournalEntryRequest.from_json(json)
# print the JSON string representation of the object
print(UpdateBasicSummaryJournalEntryRequest.to_json())

# convert the object into a dict
update_basic_summary_journal_entry_request_dict = update_basic_summary_journal_entry_request_instance.to_dict()
# create an instance of UpdateBasicSummaryJournalEntryRequest from a dict
update_basic_summary_journal_entry_request_from_dict = UpdateBasicSummaryJournalEntryRequest.from_dict(update_basic_summary_journal_entry_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


