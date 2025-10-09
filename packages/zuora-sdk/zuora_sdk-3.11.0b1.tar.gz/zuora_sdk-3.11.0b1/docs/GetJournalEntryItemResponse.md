# GetJournalEntryItemResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**accounting_code_name** | **str** | Name of the accounting code.  | [optional] 
**accounting_code_type** | [**AccountingCodeType**](AccountingCodeType.md) |  | [optional] 
**amount** | **decimal.Decimal** | Journal entry item amount in transaction currency.  | [optional] 
**gl_account_name** | **str** | The account number in the general ledger (GL) that corresponds to the accounting code.  | [optional] 
**gl_account_number** | **str** | The account name in the general ledger (GL) that corresponds to the accounting code.  | [optional] 
**gl_string** | **str** | The general ledger string. Field only available if you have GL Segmentation 2.0 enabled. | [optional] 
**home_currency_amount** | **decimal.Decimal** | Journal entry item amount in home currency.  | [optional] 
**type** | [**JournalEntryItemType**](JournalEntryItemType.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.get_journal_entry_item_response import GetJournalEntryItemResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetJournalEntryItemResponse from a JSON string
get_journal_entry_item_response_instance = GetJournalEntryItemResponse.from_json(json)
# print the JSON string representation of the object
print(GetJournalEntryItemResponse.to_json())

# convert the object into a dict
get_journal_entry_item_response_dict = get_journal_entry_item_response_instance.to_dict()
# create an instance of GetJournalEntryItemResponse from a dict
get_journal_entry_item_response_from_dict = GetJournalEntryItemResponse.from_dict(get_journal_entry_item_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


