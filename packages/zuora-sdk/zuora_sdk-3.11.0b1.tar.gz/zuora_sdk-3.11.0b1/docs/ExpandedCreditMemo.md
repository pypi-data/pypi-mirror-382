# ExpandedCreditMemo


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**applied_amount** | **float** |  | [optional] 
**balance** | **float** |  | [optional] 
**bill_to_contact_id** | **str** |  | [optional] 
**bill_to_contact_snapshot_id** | **str** |  | [optional] 
**cancelled_by_id** | **str** |  | [optional] 
**cancelled_on** | **str** |  | [optional] 
**comments** | **str** |  | [optional] 
**currency** | **str** |  | [optional] 
**discount_amount** | **float** |  | [optional] 
**e_invoice_status** | **str** |  | [optional] 
**e_invoice_file_id** | **str** |  | [optional] 
**e_invoice_error_code** | **str** |  | [optional] 
**e_invoice_error_message** | **str** |  | [optional] 
**exchange_rate_date** | **date** |  | [optional] 
**exclude_from_auto_apply_rules** | **bool** |  | [optional] 
**auto_apply_upon_posting** | **bool** |  | [optional] 
**invoice_group_number** | **str** |  | [optional] 
**memo_date** | **date** |  | [optional] 
**memo_number** | **str** |  | [optional] 
**posted_by_id** | **str** |  | [optional] 
**posted_on** | **str** |  | [optional] 
**reason_code** | **str** |  | [optional] 
**refund_amount** | **float** |  | [optional] 
**reversed** | **bool** |  | [optional] 
**revenue_impacting** | **str** |  | [optional] 
**sequence_set_id** | **str** |  | [optional] 
**communication_profile_id** | **str** |  | [optional] 
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
**source_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**debit_memo_id** | **str** |  | [optional] 
**account** | [**ExpandedAccount**](ExpandedAccount.md) |  | [optional] 
**bill_to_contact** | [**ExpandedContact**](ExpandedContact.md) |  | [optional] 
**bill_to_contact_snapshot** | [**ExpandedContactSnapshot**](ExpandedContactSnapshot.md) |  | [optional] 
**sold_to_contact_snapshot** | [**ExpandedContactSnapshot**](ExpandedContactSnapshot.md) |  | [optional] 
**ship_to_contact_snapshot** | [**ExpandedContactSnapshot**](ExpandedContactSnapshot.md) |  | [optional] 
**credit_memo_items** | [**List[ExpandedCreditMemoItem]**](ExpandedCreditMemoItem.md) |  | [optional] 
**credit_memo_applications** | [**List[ExpandedCreditMemoApplication]**](ExpandedCreditMemoApplication.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_credit_memo import ExpandedCreditMemo

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedCreditMemo from a JSON string
expanded_credit_memo_instance = ExpandedCreditMemo.from_json(json)
# print the JSON string representation of the object
print(ExpandedCreditMemo.to_json())

# convert the object into a dict
expanded_credit_memo_dict = expanded_credit_memo_instance.to_dict()
# create an instance of ExpandedCreditMemo from a dict
expanded_credit_memo_from_dict = ExpandedCreditMemo.from_dict(expanded_credit_memo_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


