# ExpandedCreditMemoItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** |  | [optional] 
**amount_without_tax** | **float** |  | [optional] 
**applied_to_item_id** | **str** |  | [optional] 
**applied_to_others_amount** | **float** |  | [optional] 
**be_applied_by_others_amount** | **float** |  | [optional] 
**charge_date** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**exclude_item_billing_from_revenue_accounting** | **bool** |  | [optional] 
**fulfillment_id** | **str** |  | [optional] 
**invoice_schedule_id** | **str** |  | [optional] 
**invoice_schedule_item_id** | **str** |  | [optional] 
**item_ship_to_contact_id** | **str** |  | [optional] 
**item_sold_to_contact_id** | **str** |  | [optional] 
**item_sold_to_contact_snapshot_id** | **str** |  | [optional] 
**item_type** | **str** |  | [optional] 
**order_line_item_id** | **str** |  | [optional] 
**processing_type** | **str** |  | [optional] 
**purchase_order_number** | **str** |  | [optional] 
**quantity** | **float** |  | [optional] 
**credit_from_item_source** | **str** |  | [optional] 
**credit_from_item_id** | **str** |  | [optional] 
**service_end_date** | **date** |  | [optional] 
**service_start_date** | **date** |  | [optional] 
**sku** | **str** |  | [optional] 
**source_item_type** | **str** |  | [optional] 
**charge_name** | **str** |  | [optional] 
**charge_number** | **str** |  | [optional] 
**commitment_charge_segment_number** | **str** |  | [optional] 
**commitment_charge_number** | **str** |  | [optional] 
**tax_amount** | **float** |  | [optional] 
**tax_code_name** | **str** |  | [optional] 
**tax_exempt_amount** | **float** |  | [optional] 
**tax_mode** | **str** |  | [optional] 
**unit_of_measure** | **str** |  | [optional] 
**unit_price** | **float** |  | [optional] 
**unapplied_amount** | **float** |  | [optional] 
**subscription_id** | **str** |  | [optional] 
**subscription_number** | **str** |  | [optional] 
**invoice_item_id** | **str** |  | [optional] 
**product_rate_plan_charge_id** | **str** |  | [optional] 
**rate_plan_charge_id** | **str** |  | [optional] 
**revenue_recognition_rule_name** | **str** |  | [optional] 
**credit_memo_id** | **str** |  | [optional] 
**number_of_deliveries** | **float** |  | [optional] 
**reflect_discount_in_net_amount** | **bool** |  | [optional] 
**revenue_impacting** | **str** |  | [optional] 
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**recognized_revenue_accounting_code_id** | **str** |  | [optional] 
**account_receivable_accounting_code_id** | **str** |  | [optional] 
**on_account_accounting_code_id** | **str** |  | [optional] 
**deferred_revenue_accounting_code_id** | **str** |  | [optional] 
**non_revenue_write_off_accounting_code_id** | **str** |  | [optional] 
**journal_entry_id** | **str** |  | [optional] 
**sold_to_contact_snapshot_id** | **str** |  | [optional] 
**bill_to_contact_snapshot_id** | **str** |  | [optional] 
**ship_to_contact_snapshot_id** | **str** |  | [optional] 
**debit_memo_item_id** | **str** |  | [optional] 
**subscription_owner_id** | **str** |  | [optional] 
**subscription** | [**ExpandedSubscription**](ExpandedSubscription.md) |  | [optional] 
**rate_plan_charge** | [**ExpandedRatePlanCharge**](ExpandedRatePlanCharge.md) |  | [optional] 
**subscription_owner** | [**ExpandedAccount**](ExpandedAccount.md) |  | [optional] 
**credit_taxation_items** | [**List[ExpandedCreditTaxationItem]**](ExpandedCreditTaxationItem.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_credit_memo_item import ExpandedCreditMemoItem

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedCreditMemoItem from a JSON string
expanded_credit_memo_item_instance = ExpandedCreditMemoItem.from_json(json)
# print the JSON string representation of the object
print(ExpandedCreditMemoItem.to_json())

# convert the object into a dict
expanded_credit_memo_item_dict = expanded_credit_memo_item_instance.to_dict()
# create an instance of ExpandedCreditMemoItem from a dict
expanded_credit_memo_item_from_dict = ExpandedCreditMemoItem.from_dict(expanded_credit_memo_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


