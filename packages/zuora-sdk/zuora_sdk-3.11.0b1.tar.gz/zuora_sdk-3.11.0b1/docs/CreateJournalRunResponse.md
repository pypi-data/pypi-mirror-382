# CreateJournalRunResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**journal_run_number** | **str** | Journal run number.  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 

## Example

```python
from zuora_sdk.models.create_journal_run_response import CreateJournalRunResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateJournalRunResponse from a JSON string
create_journal_run_response_instance = CreateJournalRunResponse.from_json(json)
# print the JSON string representation of the object
print(CreateJournalRunResponse.to_json())

# convert the object into a dict
create_journal_run_response_dict = create_journal_run_response_instance.to_dict()
# create an instance of CreateJournalRunResponse from a dict
create_journal_run_response_from_dict = CreateJournalRunResponse.from_dict(create_journal_run_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


