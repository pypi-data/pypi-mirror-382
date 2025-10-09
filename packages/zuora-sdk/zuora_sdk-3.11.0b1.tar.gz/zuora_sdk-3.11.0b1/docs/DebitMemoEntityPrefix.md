# DebitMemoEntityPrefix

Container for the prefix and starting document number of debit memos.   **Note:** This field is only available if you have the Invoice Settlement feature enabled. The Invoice Settlement feature is generally available as of Zuora Billing Release 296 (March 2021). This feature includes Unapplied Payments, Credit and Debit Memo, and Invoice Item Settlement. If you want to enable Invoice Settlement, see [Invoice Settlement Enablement and Checklist Guide](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement/Invoice_Settlement_Migration_Checklist_and_Guide) for more information.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**prefix** | **str** | The prefix of debit memos.  | [optional] 
**start_number** | **int** | The starting document number of debit memos.  | [optional] 

## Example

```python
from zuora_sdk.models.debit_memo_entity_prefix import DebitMemoEntityPrefix

# TODO update the JSON string below
json = "{}"
# create an instance of DebitMemoEntityPrefix from a JSON string
debit_memo_entity_prefix_instance = DebitMemoEntityPrefix.from_json(json)
# print the JSON string representation of the object
print(DebitMemoEntityPrefix.to_json())

# convert the object into a dict
debit_memo_entity_prefix_dict = debit_memo_entity_prefix_instance.to_dict()
# create an instance of DebitMemoEntityPrefix from a dict
debit_memo_entity_prefix_from_dict = DebitMemoEntityPrefix.from_dict(debit_memo_entity_prefix_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


