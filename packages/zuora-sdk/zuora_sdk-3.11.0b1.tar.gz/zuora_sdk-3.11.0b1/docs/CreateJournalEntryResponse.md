# CreateJournalEntryResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**journal_entry_number** | **str** | Journal entry number in the format JE-00000001.  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 

## Example

```python
from zuora_sdk.models.create_journal_entry_response import CreateJournalEntryResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateJournalEntryResponse from a JSON string
create_journal_entry_response_instance = CreateJournalEntryResponse.from_json(json)
# print the JSON string representation of the object
print(CreateJournalEntryResponse.to_json())

# convert the object into a dict
create_journal_entry_response_dict = create_journal_entry_response_instance.to_dict()
# create an instance of CreateJournalEntryResponse from a dict
create_journal_entry_response_from_dict = CreateJournalEntryResponse.from_dict(create_journal_entry_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


