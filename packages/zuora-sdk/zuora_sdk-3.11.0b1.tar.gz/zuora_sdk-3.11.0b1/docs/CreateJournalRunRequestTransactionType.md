# CreateJournalRunRequestTransactionType


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | [**JournalRunTransactionType**](JournalRunTransactionType.md) |  | 

## Example

```python
from zuora_sdk.models.create_journal_run_request_transaction_type import CreateJournalRunRequestTransactionType

# TODO update the JSON string below
json = "{}"
# create an instance of CreateJournalRunRequestTransactionType from a JSON string
create_journal_run_request_transaction_type_instance = CreateJournalRunRequestTransactionType.from_json(json)
# print the JSON string representation of the object
print(CreateJournalRunRequestTransactionType.to_json())

# convert the object into a dict
create_journal_run_request_transaction_type_dict = create_journal_run_request_transaction_type_instance.to_dict()
# create an instance of CreateJournalRunRequestTransactionType from a dict
create_journal_run_request_transaction_type_from_dict = CreateJournalRunRequestTransactionType.from_dict(create_journal_run_request_transaction_type_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


