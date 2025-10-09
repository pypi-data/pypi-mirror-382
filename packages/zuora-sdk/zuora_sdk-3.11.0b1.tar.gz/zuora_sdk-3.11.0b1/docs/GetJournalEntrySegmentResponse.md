# GetJournalEntrySegmentResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**segment_name** | **str** | Name of segment.  | [optional] 
**segment_value** | **str** | Value of segment in this summary journal entry.  | [optional] 

## Example

```python
from zuora_sdk.models.get_journal_entry_segment_response import GetJournalEntrySegmentResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetJournalEntrySegmentResponse from a JSON string
get_journal_entry_segment_response_instance = GetJournalEntrySegmentResponse.from_json(json)
# print the JSON string representation of the object
print(GetJournalEntrySegmentResponse.to_json())

# convert the object into a dict
get_journal_entry_segment_response_dict = get_journal_entry_segment_response_instance.to_dict()
# create an instance of GetJournalEntrySegmentResponse from a dict
get_journal_entry_segment_response_from_dict = GetJournalEntrySegmentResponse.from_dict(get_journal_entry_segment_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


