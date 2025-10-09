# CreditMemoEntityPrefix

Container for the prefix and starting document number of credit memos.   **Note:** This field is only available if you have the Invoice Settlement feature enabled. The Invoice Settlement feature is generally available as of Zuora Billing Release 296 (March 2021). This feature includes Unapplied Payments, Credit and Debit Memo, and Invoice Item Settlement. If you want to enable Invoice Settlement, see [Invoice Settlement Enablement and Checklist Guide](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement/Invoice_Settlement_Migration_Checklist_and_Guide) for more information.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**prefix** | **str** | The prefix of credit memos.  | [optional] 
**start_number** | **int** | The starting document number of credit memos.  | [optional] 

## Example

```python
from zuora_sdk.models.credit_memo_entity_prefix import CreditMemoEntityPrefix

# TODO update the JSON string below
json = "{}"
# create an instance of CreditMemoEntityPrefix from a JSON string
credit_memo_entity_prefix_instance = CreditMemoEntityPrefix.from_json(json)
# print the JSON string representation of the object
print(CreditMemoEntityPrefix.to_json())

# convert the object into a dict
credit_memo_entity_prefix_dict = credit_memo_entity_prefix_instance.to_dict()
# create an instance of CreditMemoEntityPrefix from a dict
credit_memo_entity_prefix_from_dict = CreditMemoEntityPrefix.from_dict(credit_memo_entity_prefix_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


