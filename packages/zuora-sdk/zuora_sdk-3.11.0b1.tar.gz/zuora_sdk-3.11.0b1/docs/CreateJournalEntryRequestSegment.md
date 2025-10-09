# CreateJournalEntryRequestSegment


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**segment_name** | **str** | Name of segment. You must use the segment name that has already been specified in the default segment rule. In addition, segments need to be passed in the order where they were defined in the segmentation rule. If multiple segments are configured in the default rule, you need to specify all of them in order.  | 
**segment_value** | **str** | Value of segment in this summary journal entry.  | 

## Example

```python
from zuora_sdk.models.create_journal_entry_request_segment import CreateJournalEntryRequestSegment

# TODO update the JSON string below
json = "{}"
# create an instance of CreateJournalEntryRequestSegment from a JSON string
create_journal_entry_request_segment_instance = CreateJournalEntryRequestSegment.from_json(json)
# print the JSON string representation of the object
print(CreateJournalEntryRequestSegment.to_json())

# convert the object into a dict
create_journal_entry_request_segment_dict = create_journal_entry_request_segment_instance.to_dict()
# create an instance of CreateJournalEntryRequestSegment from a dict
create_journal_entry_request_segment_from_dict = CreateJournalEntryRequestSegment.from_dict(create_journal_entry_request_segment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


