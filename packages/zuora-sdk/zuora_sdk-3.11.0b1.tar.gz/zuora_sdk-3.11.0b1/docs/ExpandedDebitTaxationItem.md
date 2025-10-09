# ExpandedDebitTaxationItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**accounting_code** | **str** |  | [optional] 
**balance** | **float** |  | [optional] 
**credit_amount** | **float** |  | [optional] 
**exempt_amount** | **float** |  | [optional] 
**jurisdiction** | **str** |  | [optional] 
**location_code** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**payment_amount** | **float** |  | [optional] 
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
**debit_memo_item_id** | **str** |  | [optional] 
**taxable_item_snapshot_id** | **str** |  | [optional] 
**taxation_item_id** | **str** |  | [optional] 
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**account_receivable_accounting_code_id** | **str** |  | [optional] 
**journal_entry_id** | **str** |  | [optional] 
**sales_tax_payable_accounting_code_id** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_debit_taxation_item import ExpandedDebitTaxationItem

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedDebitTaxationItem from a JSON string
expanded_debit_taxation_item_instance = ExpandedDebitTaxationItem.from_json(json)
# print the JSON string representation of the object
print(ExpandedDebitTaxationItem.to_json())

# convert the object into a dict
expanded_debit_taxation_item_dict = expanded_debit_taxation_item_instance.to_dict()
# create an instance of ExpandedDebitTaxationItem from a dict
expanded_debit_taxation_item_from_dict = ExpandedDebitTaxationItem.from_dict(expanded_debit_taxation_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


