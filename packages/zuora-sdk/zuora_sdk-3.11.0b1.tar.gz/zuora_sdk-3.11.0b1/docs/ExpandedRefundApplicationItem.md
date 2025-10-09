# ExpandedRefundApplicationItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** |  | [optional] 
**effective_date** | **date** |  | [optional] 
**application_group_id** | **str** |  | [optional] 
**refund_application_id** | **str** |  | [optional] 
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**on_account_accounting_code_id** | **str** |  | [optional] 
**journal_entry_id** | **str** |  | [optional] 
**cash_accounting_code_id** | **str** |  | [optional] 
**unapplied_payment_accounting_code_id** | **str** |  | [optional] 
**account_receivable_accounting_code_id** | **str** |  | [optional] 
**credit_taxation_item_id** | **str** |  | [optional] 
**credit_memo_item_id** | **str** |  | [optional] 
**refund_application** | [**ExpandedRefundApplication**](ExpandedRefundApplication.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_refund_application_item import ExpandedRefundApplicationItem

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedRefundApplicationItem from a JSON string
expanded_refund_application_item_instance = ExpandedRefundApplicationItem.from_json(json)
# print the JSON string representation of the object
print(ExpandedRefundApplicationItem.to_json())

# convert the object into a dict
expanded_refund_application_item_dict = expanded_refund_application_item_instance.to_dict()
# create an instance of ExpandedRefundApplicationItem from a dict
expanded_refund_application_item_from_dict = ExpandedRefundApplicationItem.from_dict(expanded_refund_application_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


