# UpdateJournalEntryItemRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**accounting_code_name** | **str** | Name of the accounting code.  If the Journal Entry Item has a blank accounting code, enter the empty string.  | 
**accounting_code_type** | [**AccountingCodeType**](AccountingCodeType.md) |  | [optional] 
**type** | [**JournalEntryItemType**](JournalEntryItemType.md) |  | 

## Example

```python
from zuora_sdk.models.update_journal_entry_item_request import UpdateJournalEntryItemRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateJournalEntryItemRequest from a JSON string
update_journal_entry_item_request_instance = UpdateJournalEntryItemRequest.from_json(json)
# print the JSON string representation of the object
print(UpdateJournalEntryItemRequest.to_json())

# convert the object into a dict
update_journal_entry_item_request_dict = update_journal_entry_item_request_instance.to_dict()
# create an instance of UpdateJournalEntryItemRequest from a dict
update_journal_entry_item_request_from_dict = UpdateJournalEntryItemRequest.from_dict(update_journal_entry_item_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


