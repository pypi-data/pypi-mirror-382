# ExpandedDebitMemo


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**auto_pay** | **bool** |  | [optional] 
**balance** | **float** |  | [optional] 
**bill_to_contact_id** | **str** |  | [optional] 
**bill_to_contact_snapshot_id** | **str** |  | [optional] 
**cancelled_by_id** | **str** |  | [optional] 
**cancelled_on** | **str** |  | [optional] 
**comments** | **str** |  | [optional] 
**credit_memo_id** | **str** |  | [optional] 
**currency** | **str** |  | [optional] 
**discount_amount** | **float** |  | [optional] 
**due_date** | **date** |  | [optional] 
**e_invoice_status** | **str** |  | [optional] 
**e_invoice_file_id** | **str** |  | [optional] 
**e_invoice_error_code** | **str** |  | [optional] 
**e_invoice_error_message** | **str** |  | [optional] 
**exchange_rate_date** | **date** |  | [optional] 
**invoice_group_number** | **str** |  | [optional] 
**communication_profile_id** | **str** |  | [optional] 
**memo_date** | **date** |  | [optional] 
**memo_number** | **str** |  | [optional] 
**posted_by_id** | **str** |  | [optional] 
**posted_on** | **str** |  | [optional] 
**reason_code** | **str** |  | [optional] 
**referred_debit_memo_id** | **str** |  | [optional] 
**sequence_set_id** | **str** |  | [optional] 
**ship_to_contact_snapshot_id** | **str** |  | [optional] 
**sold_to_contact_snapshot_id** | **str** |  | [optional] 
**source** | **str** |  | [optional] 
**source_type** | **str** |  | [optional] 
**status** | **str** |  | [optional] 
**target_date** | **date** |  | [optional] 
**tax_amount** | **float** |  | [optional] 
**tax_auto_calculation** | **bool** |  | [optional] 
**tax_message** | **str** |  | [optional] 
**tax_status** | **str** |  | [optional] 
**total_amount** | **float** |  | [optional] 
**total_amount_without_tax** | **float** |  | [optional] 
**total_tax_exempt_amount** | **float** |  | [optional] 
**transferred_to_accounting** | **str** |  | [optional] 
**invoice_id** | **str** |  | [optional] 
**account_id** | **str** |  | [optional] 
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**sold_to_contact_id** | **str** |  | [optional] 
**payment_term** | **str** |  | [optional] 
**account** | [**ExpandedAccount**](ExpandedAccount.md) |  | [optional] 
**bill_to_contact** | [**ExpandedContact**](ExpandedContact.md) |  | [optional] 
**bill_to_contact_snapshot** | [**ExpandedContactSnapshot**](ExpandedContactSnapshot.md) |  | [optional] 
**sold_to_contact_snapshot** | [**ExpandedContactSnapshot**](ExpandedContactSnapshot.md) |  | [optional] 
**ship_to_contact_snapshot** | [**ExpandedContactSnapshot**](ExpandedContactSnapshot.md) |  | [optional] 
**debit_memo_items** | [**List[ExpandedDebitMemoItem]**](ExpandedDebitMemoItem.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_debit_memo import ExpandedDebitMemo

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedDebitMemo from a JSON string
expanded_debit_memo_instance = ExpandedDebitMemo.from_json(json)
# print the JSON string representation of the object
print(ExpandedDebitMemo.to_json())

# convert the object into a dict
expanded_debit_memo_dict = expanded_debit_memo_instance.to_dict()
# create an instance of ExpandedDebitMemo from a dict
expanded_debit_memo_from_dict = ExpandedDebitMemo.from_dict(expanded_debit_memo_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


