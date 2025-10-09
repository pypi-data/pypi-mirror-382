# CreateJournalEntryRequestItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**accounting_code_name** | **str** | Name of the accounting code.  | 
**accounting_code_type** | [**AccountingCodeType**](AccountingCodeType.md) |  | [optional] 
**amount** | **decimal.Decimal** | Journal entry item amount in transaction currency.  | 
**home_currency_amount** | **decimal.Decimal** | Journal entry item amount in home currency.  This field is required if you have set your home currency for foreign currency conversion. Otherwise, do not pass this field.  | [optional] 
**type** | [**JournalEntryItemType**](JournalEntryItemType.md) |  | 

## Example

```python
from zuora_sdk.models.create_journal_entry_request_item import CreateJournalEntryRequestItem

# TODO update the JSON string below
json = "{}"
# create an instance of CreateJournalEntryRequestItem from a JSON string
create_journal_entry_request_item_instance = CreateJournalEntryRequestItem.from_json(json)
# print the JSON string representation of the object
print(CreateJournalEntryRequestItem.to_json())

# convert the object into a dict
create_journal_entry_request_item_dict = create_journal_entry_request_item_instance.to_dict()
# create an instance of CreateJournalEntryRequestItem from a dict
create_journal_entry_request_item_from_dict = CreateJournalEntryRequestItem.from_dict(create_journal_entry_request_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


