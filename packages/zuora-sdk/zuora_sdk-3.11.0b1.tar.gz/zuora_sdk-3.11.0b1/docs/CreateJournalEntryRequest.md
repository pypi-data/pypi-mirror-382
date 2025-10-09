# CreateJournalEntryRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**accounting_period_name** | **str** | Name of the accounting period. The open-ended accounting period is named &#x60;Open-Ended&#x60;.  | 
**currency** | **str** | The type of currency used. Currency must be active.  | 
**journal_entry_date** | **date** | Date of the journal entry.  | 
**journal_entry_items** | [**List[CreateJournalEntryRequestItem]**](CreateJournalEntryRequestItem.md) | Key name that represents the list of journal entry items.  | 
**notes** | **str** | The number associated with the revenue event.  Character limit: 2,000  | [optional] 
**organization_label** | **str** | Organization Label  | [optional] 
**segments** | [**List[CreateJournalEntryRequestSegment]**](CreateJournalEntryRequestSegment.md) | List of segments that apply to the summary journal entry.  | [optional] 
**transferred_to_accounting** | [**TransferredToAccountingStatus**](TransferredToAccountingStatus.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.create_journal_entry_request import CreateJournalEntryRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateJournalEntryRequest from a JSON string
create_journal_entry_request_instance = CreateJournalEntryRequest.from_json(json)
# print the JSON string representation of the object
print(CreateJournalEntryRequest.to_json())

# convert the object into a dict
create_journal_entry_request_dict = create_journal_entry_request_instance.to_dict()
# create an instance of CreateJournalEntryRequest from a dict
create_journal_entry_request_from_dict = CreateJournalEntryRequest.from_dict(create_journal_entry_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


