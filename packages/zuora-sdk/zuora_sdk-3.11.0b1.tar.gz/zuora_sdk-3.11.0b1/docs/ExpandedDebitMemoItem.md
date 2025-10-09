# ExpandedDebitMemoItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** |  | [optional] 
**amount_without_tax** | **float** |  | [optional] 
**applied_to_item_id** | **str** |  | [optional] 
**applied_to_others_amount** | **float** |  | [optional] 
**be_applied_by_others_amount** | **float** |  | [optional] 
**charge_date** | **str** |  | [optional] 
**credit_memo_item_id** | **str** |  | [optional] 
**exclude_item_billing_from_revenue_accounting** | **bool** |  | [optional] 
**description** | **str** |  | [optional] 
**item_ship_to_contact_id** | **str** |  | [optional] 
**item_sold_to_contact_id** | **str** |  | [optional] 
**item_sold_to_contact_snapshot_id** | **str** |  | [optional] 
**processing_type** | **str** |  | [optional] 
**quantity** | **float** |  | [optional] 
**service_end_date** | **date** |  | [optional] 
**service_start_date** | **date** |  | [optional] 
**sku** | **str** |  | [optional] 
**source_item_type** | **str** |  | [optional] 
**charge_name** | **str** |  | [optional] 
**charge_number** | **str** |  | [optional] 
**tax_amount** | **float** |  | [optional] 
**tax_code_name** | **str** |  | [optional] 
**tax_exempt_amount** | **float** |  | [optional] 
**tax_mode** | **str** |  | [optional] 
**unit_of_measure** | **str** |  | [optional] 
**unit_price** | **float** |  | [optional] 
**subscription_id** | **str** |  | [optional] 
**subscription_number** | **str** |  | [optional] 
**invoice_item_id** | **str** |  | [optional] 
**product_rate_plan_charge_id** | **str** |  | [optional] 
**rate_plan_charge_id** | **str** |  | [optional] 
**debit_memo_id** | **str** |  | [optional] 
**balance** | **float** |  | [optional] 
**reflect_discount_in_net_amount** | **bool** |  | [optional] 
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**recognized_revenue_accounting_code_id** | **str** |  | [optional] 
**account_receivable_accounting_code_id** | **str** |  | [optional] 
**deferred_revenue_accounting_code_id** | **str** |  | [optional] 
**journal_entry_id** | **str** |  | [optional] 
**sold_to_contact_snapshot_id** | **str** |  | [optional] 
**bill_to_contact_snapshot_id** | **str** |  | [optional] 
**ship_to_contact_snapshot_id** | **str** |  | [optional] 
**subscription_owner_id** | **str** |  | [optional] 
**subscription** | [**ExpandedSubscription**](ExpandedSubscription.md) |  | [optional] 
**rate_plan_charge** | [**ExpandedRatePlanCharge**](ExpandedRatePlanCharge.md) |  | [optional] 
**subscription_owner** | [**ExpandedAccount**](ExpandedAccount.md) |  | [optional] 
**debit_taxation_items** | [**List[ExpandedDebitTaxationItem]**](ExpandedDebitTaxationItem.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_debit_memo_item import ExpandedDebitMemoItem

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedDebitMemoItem from a JSON string
expanded_debit_memo_item_instance = ExpandedDebitMemoItem.from_json(json)
# print the JSON string representation of the object
print(ExpandedDebitMemoItem.to_json())

# convert the object into a dict
expanded_debit_memo_item_dict = expanded_debit_memo_item_instance.to_dict()
# create an instance of ExpandedDebitMemoItem from a dict
expanded_debit_memo_item_from_dict = ExpandedDebitMemoItem.from_dict(expanded_debit_memo_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


