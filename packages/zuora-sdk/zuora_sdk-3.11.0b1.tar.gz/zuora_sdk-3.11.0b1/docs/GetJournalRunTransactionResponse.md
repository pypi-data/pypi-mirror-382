# GetJournalRunTransactionResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | [**JournalRunTransactionType**](JournalRunTransactionType.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.get_journal_run_transaction_response import GetJournalRunTransactionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetJournalRunTransactionResponse from a JSON string
get_journal_run_transaction_response_instance = GetJournalRunTransactionResponse.from_json(json)
# print the JSON string representation of the object
print(GetJournalRunTransactionResponse.to_json())

# convert the object into a dict
get_journal_run_transaction_response_dict = get_journal_run_transaction_response_instance.to_dict()
# create an instance of GetJournalRunTransactionResponse from a dict
get_journal_run_transaction_response_from_dict = GetJournalRunTransactionResponse.from_dict(get_journal_run_transaction_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


