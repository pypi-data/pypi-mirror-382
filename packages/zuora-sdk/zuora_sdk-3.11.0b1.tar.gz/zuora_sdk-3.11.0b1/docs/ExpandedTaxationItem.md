# ExpandedTaxationItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**credit_amount** | **float** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**accounting_code** | **str** |  | [optional] 
**exempt_amount** | **float** |  | [optional] 
**invoice_item_id** | **str** |  | [optional] 
**jurisdiction** | **str** |  | [optional] 
**location_code** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**payment_amount** | **float** |  | [optional] 
**taxable_amount** | **float** |  | [optional] 
**tax_amount** | **float** |  | [optional] 
**tax_amount_unrounded** | **float** |  | [optional] 
**country_code** | **str** |  | [optional] 
**tax_code_description** | **str** |  | [optional] 
**customer_code** | **str** |  | [optional] 
**exempt_certificate** | **str** |  | [optional] 
**seller_registration** | **str** |  | [optional] 
**tax_description** | **str** |  | [optional] 
**tax_rule_id** | **str** |  | [optional] 
**tax_code** | **str** |  | [optional] 
**tax_mode** | **str** |  | [optional] 
**tax_date** | **date** |  | [optional] 
**period_end_date** | **date** |  | [optional] 
**period_start_date** | **date** |  | [optional] 
**tax_rate** | **float** |  | [optional] 
**tax_rate_description** | **str** |  | [optional] 
**tax_rate_type** | **str** |  | [optional] 
**balance** | **float** |  | [optional] 
**journal_entry_id** | **str** |  | [optional] 
**sales_tax_payable_accounting_code_id** | **str** |  | [optional] 
**account_receivable_accounting_code_id** | **str** |  | [optional] 
**taxable_item_snapshot_id** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_taxation_item import ExpandedTaxationItem

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedTaxationItem from a JSON string
expanded_taxation_item_instance = ExpandedTaxationItem.from_json(json)
# print the JSON string representation of the object
print(ExpandedTaxationItem.to_json())

# convert the object into a dict
expanded_taxation_item_dict = expanded_taxation_item_instance.to_dict()
# create an instance of ExpandedTaxationItem from a dict
expanded_taxation_item_from_dict = ExpandedTaxationItem.from_dict(expanded_taxation_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


