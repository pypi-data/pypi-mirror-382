# ExpandedCreditTaxationItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**accounting_code** | **str** |  | [optional] 
**applied_amount** | **float** |  | [optional] 
**exempt_amount** | **float** |  | [optional] 
**jurisdiction** | **str** |  | [optional] 
**location_code** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**refund_amount** | **float** |  | [optional] 
**taxable_amount** | **float** |  | [optional] 
**tax_amount** | **float** |  | [optional] 
**tax_code** | **str** |  | [optional] 
**tax_code_description** | **str** |  | [optional] 
**tax_date** | **date** |  | [optional] 
**period_end_date** | **date** |  | [optional] 
**period_start_date** | **date** |  | [optional] 
**tax_mode** | **str** |  | [optional] 
**tax_rate** | **float** |  | [optional] 
**tax_rate_description** | **str** |  | [optional] 
**tax_rate_type** | **str** |  | [optional] 
**unapplied_amount** | **float** |  | [optional] 
**credit_memo_item_id** | **str** |  | [optional] 
**taxable_item_snapshot_id** | **str** |  | [optional] 
**taxation_item_id** | **str** |  | [optional] 
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**account_receivable_accounting_code_id** | **str** |  | [optional] 
**journal_entry_id** | **str** |  | [optional] 
**on_account_accounting_code_id** | **str** |  | [optional] 
**sales_tax_payable_accounting_code_id** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_credit_taxation_item import ExpandedCreditTaxationItem

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedCreditTaxationItem from a JSON string
expanded_credit_taxation_item_instance = ExpandedCreditTaxationItem.from_json(json)
# print the JSON string representation of the object
print(ExpandedCreditTaxationItem.to_json())

# convert the object into a dict
expanded_credit_taxation_item_dict = expanded_credit_taxation_item_instance.to_dict()
# create an instance of ExpandedCreditTaxationItem from a dict
expanded_credit_taxation_item_from_dict = ExpandedCreditTaxationItem.from_dict(expanded_credit_taxation_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


