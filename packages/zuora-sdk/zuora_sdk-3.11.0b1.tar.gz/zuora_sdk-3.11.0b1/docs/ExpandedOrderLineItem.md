# ExpandedOrderLineItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**accounting_code** | **str** |  | [optional] 
**bill_target_date** | **date** |  | [optional] 
**currency** | **str** |  | [optional] 
**sequence_set_id** | **str** |  | [optional] 
**payment_term** | **str** |  | [optional] 
**invoice_template_id** | **str** |  | [optional] 
**communication_profile_id** | **str** |  | [optional] 
**amount_per_unit** | **float** |  | [optional] 
**description** | **str** |  | [optional] 
**amount** | **float** |  | [optional] 
**amount_without_tax** | **float** |  | [optional] 
**invoice_group_number** | **str** |  | [optional] 
**item_name** | **str** |  | [optional] 
**item_number** | **str** |  | [optional] 
**item_state** | **str** |  | [optional] 
**item_type** | **str** |  | [optional] 
**list_price_per_unit** | **float** |  | [optional] 
**list_price** | **float** |  | [optional] 
**order_id** | **str** |  | [optional] 
**product_code** | **str** |  | [optional] 
**purchase_order_number** | **str** |  | [optional] 
**quantity** | **float** |  | [optional] 
**revenue_recognition_rule** | **str** |  | [optional] 
**product_rate_plan_charge_id** | **str** |  | [optional] 
**bill_to_id** | **str** |  | [optional] 
**bill_to_snapshot_id** | **str** |  | [optional] 
**sold_to** | **str** |  | [optional] 
**sold_to_info_id** | **str** |  | [optional] 
**sold_to_snapshot_id** | **str** |  | [optional] 
**sold_to_order_contact_id** | **str** |  | [optional] 
**ship_to_id** | **str** |  | [optional] 
**ship_to_snapshot_id** | **str** |  | [optional] 
**owner_account_id** | **str** |  | [optional] 
**invoice_owner_account_id** | **str** |  | [optional] 
**tax_code** | **str** |  | [optional] 
**tax_mode** | **str** |  | [optional] 
**transaction_date** | **date** |  | [optional] 
**u_om** | **str** |  | [optional] 
**related_subscription_number** | **str** |  | [optional] 
**transaction_start_date** | **date** |  | [optional] 
**transaction_end_date** | **date** |  | [optional] 
**exclude_item_booking_from_revenue_accounting** | **bool** |  | [optional] 
**exclude_item_billing_from_revenue_accounting** | **bool** |  | [optional] 
**is_allocation_eligible** | **bool** |  | [optional] 
**is_unbilled** | **bool** |  | [optional] 
**revenue_recognition_timing** | **str** |  | [optional] 
**revenue_amortization_method** | **str** |  | [optional] 
**original_order_date** | **date** |  | [optional] 
**amended_by_order_on** | **date** |  | [optional] 
**item_category** | **str** |  | [optional] 
**original_order_id** | **str** |  | [optional] 
**original_order_number** | **str** |  | [optional] 
**original_order_line_item_id** | **str** |  | [optional] 
**original_order_line_item_number** | **str** |  | [optional] 
**quantity_fulfilled** | **float** |  | [optional] 
**quantity_pending_fulfillment** | **float** |  | [optional] 
**quantity_available_for_return** | **float** |  | [optional] 
**requires_fulfillment** | **bool** |  | [optional] 
**billing_rule** | **str** |  | [optional] 
**inline_discount_per_unit** | **float** |  | [optional] 
**inline_discount_type** | **str** |  | [optional] 
**discount** | **float** |  | [optional] 
**recognized_revenue_accounting_code_id** | **str** |  | [optional] 
**deferred_revenue_accounting_code_id** | **str** |  | [optional] 
**contract_asset_accounting_code_id** | **str** |  | [optional] 
**contract_liability_accounting_code_id** | **str** |  | [optional] 
**contract_recognized_revenue_accounting_code_id** | **str** |  | [optional] 
**unbilled_receivables_accounting_code_id** | **str** |  | [optional] 
**adjustment_revenue_accounting_code_id** | **str** |  | [optional] 
**adjustment_liability_accounting_code_id** | **str** |  | [optional] 
**invoice_items** | [**List[ExpandedInvoiceItem]**](ExpandedInvoiceItem.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_order_line_item import ExpandedOrderLineItem

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedOrderLineItem from a JSON string
expanded_order_line_item_instance = ExpandedOrderLineItem.from_json(json)
# print the JSON string representation of the object
print(ExpandedOrderLineItem.to_json())

# convert the object into a dict
expanded_order_line_item_dict = expanded_order_line_item_instance.to_dict()
# create an instance of ExpandedOrderLineItem from a dict
expanded_order_line_item_from_dict = ExpandedOrderLineItem.from_dict(expanded_order_line_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


