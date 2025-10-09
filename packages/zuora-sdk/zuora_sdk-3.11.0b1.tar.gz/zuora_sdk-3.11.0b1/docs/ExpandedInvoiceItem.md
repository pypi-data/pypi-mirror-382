# ExpandedInvoiceItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**invoice_id** | **str** |  | [optional] 
**invoice_schedule_id** | **str** |  | [optional] 
**invoice_schedule_item_id** | **str** |  | [optional] 
**rate_plan_charge_id** | **str** |  | [optional] 
**product_rate_plan_charge_id** | **str** |  | [optional] 
**accounting_code** | **str** |  | [optional] 
**applied_to_invoice_item_id** | **str** |  | [optional] 
**charge_amount** | **float** |  | [optional] 
**charge_date** | **str** |  | [optional] 
**charge_name** | **str** |  | [optional] 
**charge_number** | **str** |  | [optional] 
**commitment_charge_number** | **str** |  | [optional] 
**commitment_charge_segment_number** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**discount_amount** | **float** |  | [optional] 
**exclude_item_billing_from_revenue_accounting** | **bool** |  | [optional] 
**fulfillment_id** | **str** |  | [optional] 
**item_ship_to_contact_id** | **str** |  | [optional] 
**item_sold_to_contact_id** | **str** |  | [optional] 
**item_sold_to_contact_snapshot_id** | **str** |  | [optional] 
**processing_type** | **str** |  | [optional] 
**quantity** | **float** |  | [optional] 
**reflect_discount_in_net_amount** | **bool** |  | [optional] 
**rev_rec_start_date** | **date** |  | [optional] 
**service_end_date** | **date** |  | [optional] 
**service_start_date** | **date** |  | [optional] 
**s_ku** | **str** |  | [optional] 
**source_item_type** | **str** |  | [optional] 
**order_line_item_id** | **str** |  | [optional] 
**subscription_id** | **str** |  | [optional] 
**subscription_number** | **str** |  | [optional] 
**tax_amount** | **float** |  | [optional] 
**tax_code** | **str** |  | [optional] 
**tax_exempt_amount** | **float** |  | [optional] 
**tax_mode** | **str** |  | [optional] 
**unit_price** | **float** |  | [optional] 
**u_om** | **str** |  | [optional] 
**balance** | **float** |  | [optional] 
**number_of_deliveries** | **float** |  | [optional] 
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**account_receivable_accounting_code_id** | **str** |  | [optional] 
**recognized_revenue_accounting_code_id** | **str** |  | [optional] 
**deferred_revenue_accounting_code_id** | **str** |  | [optional] 
**contract_asset_accounting_code_id** | **str** |  | [optional] 
**contract_liability_accounting_code_id** | **str** |  | [optional] 
**contract_recognized_revenue_accounting_code_id** | **str** |  | [optional] 
**unbilled_receivables_accounting_code_id** | **str** |  | [optional] 
**adjustment_revenue_accounting_code_id** | **str** |  | [optional] 
**adjustment_liability_accounting_code_id** | **str** |  | [optional] 
**journal_entry_id** | **str** |  | [optional] 
**account_id** | **str** |  | [optional] 
**bill_to_contact_snapshot_id** | **str** |  | [optional] 
**sold_to_contact_snapshot_id** | **str** |  | [optional] 
**ship_to_contact_snapshot_id** | **str** |  | [optional] 
**parent_account_id** | **str** |  | [optional] 
**bill_to_contact_id** | **str** |  | [optional] 
**sold_to_contact_id** | **str** |  | [optional] 
**ship_to_contact_id** | **str** |  | [optional] 
**default_payment_method_id** | **str** |  | [optional] 
**rate_plan_id** | **str** |  | [optional] 
**amendment_id** | **str** |  | [optional] 
**product_rate_plan_id** | **str** |  | [optional] 
**product_id** | **str** |  | [optional] 
**subscription_owner_id** | **str** |  | [optional] 
**booking_reference** | **str** |  | [optional] 
**item_type** | **str** |  | [optional] 
**purchase_order_number** | **str** |  | [optional] 
**rev_rec_code** | **str** |  | [optional] 
**rev_rec_trigger_condition** | **str** |  | [optional] 
**revenue_recognition_rule_name** | **str** |  | [optional] 
**invoice** | [**ExpandedInvoice**](ExpandedInvoice.md) |  | [optional] 
**subscription** | [**ExpandedSubscription**](ExpandedSubscription.md) |  | [optional] 
**subscription_owner** | [**ExpandedAccount**](ExpandedAccount.md) |  | [optional] 
**taxation_items** | [**List[ExpandedTaxationItem]**](ExpandedTaxationItem.md) |  | [optional] 
**rate_plan_charge** | [**ExpandedRatePlanCharge**](ExpandedRatePlanCharge.md) |  | [optional] 
**order_line_item** | [**ExpandedOrderLineItem**](ExpandedOrderLineItem.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_invoice_item import ExpandedInvoiceItem

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedInvoiceItem from a JSON string
expanded_invoice_item_instance = ExpandedInvoiceItem.from_json(json)
# print the JSON string representation of the object
print(ExpandedInvoiceItem.to_json())

# convert the object into a dict
expanded_invoice_item_dict = expanded_invoice_item_instance.to_dict()
# create an instance of ExpandedInvoiceItem from a dict
expanded_invoice_item_from_dict = ExpandedInvoiceItem.from_dict(expanded_invoice_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


