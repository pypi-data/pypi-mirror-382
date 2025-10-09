# ExpandedRatePlanCharge


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**rate_plan_id** | **str** |  | [optional] 
**product_rate_plan_charge_id** | **str** |  | [optional] 
**accounting_code** | **str** |  | [optional] 
**accounting_code_entity_id** | **int** |  | [optional] 
**apply_discount_to** | **str** |  | [optional] 
**bill_cycle_day** | **int** |  | [optional] 
**bill_cycle_type** | **str** |  | [optional] 
**billing_period** | **str** |  | [optional] 
**billing_period_alignment** | **str** |  | [optional] 
**billing_timing** | **str** |  | [optional] 
**charged_through_date** | **date** |  | [optional] 
**charge_function** | **str** |  | [optional] 
**charge_model** | **str** |  | [optional] 
**charge_number** | **str** |  | [optional] 
**charge_type** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**discount_level** | **str** |  | [optional] 
**d_mrc** | **float** |  | [optional] 
**drawdown_rate** | **float** |  | [optional] 
**d_tcv** | **float** |  | [optional] 
**effective_end_date** | **date** |  | [optional] 
**effective_start_date** | **date** |  | [optional] 
**end_date_condition** | **str** |  | [optional] 
**exclude_item_booking_from_revenue_accounting** | **bool** |  | [optional] 
**reflect_discount_in_net_amount** | **bool** |  | [optional] 
**revenue_recognition_timing** | **str** |  | [optional] 
**revenue_amortization_method** | **str** |  | [optional] 
**exclude_item_billing_from_revenue_accounting** | **bool** |  | [optional] 
**invoice_schedule_id** | **str** |  | [optional] 
**is_last_segment** | **bool** |  | [optional] 
**is_prepaid** | **bool** |  | [optional] 
**is_rollover** | **bool** |  | [optional] 
**rollover_periods** | **int** |  | [optional] 
**rollover_period_length** | **int** |  | [optional] 
**rollover_apply** | **str** |  | [optional] 
**is_processed** | **bool** |  | [optional] 
**list_price_base** | **str** |  | [optional] 
**specific_list_price_base** | **int** |  | [optional] 
**price_upsell_quantity_stacked** | **bool** |  | [optional] 
**commitment_type** | **str** |  | [optional] 
**is_committed** | **bool** |  | [optional] 
**m_rr** | **float** |  | [optional] 
**name** | **str** |  | [optional] 
**number_of_periods** | **int** |  | [optional] 
**original_id** | **str** |  | [optional] 
**overage_calculation_option** | **str** |  | [optional] 
**overage_unused_units_credit_option** | **str** |  | [optional] 
**prepaid_operation_type** | **str** |  | [optional] 
**prepaid_quantity** | **float** |  | [optional] 
**prepaid_total_quantity** | **float** |  | [optional] 
**sales_price** | **float** |  | [optional] 
**estimated_start_date** | **date** |  | [optional] 
**estimated_end_date** | **date** |  | [optional] 
**price_change_option** | **str** |  | [optional] 
**price_increase_percentage** | **float** |  | [optional] 
**processed_through_date** | **date** |  | [optional] 
**proration_option** | **str** |  | [optional] 
**quantity** | **float** |  | [optional] 
**number_of_deliveries** | **float** |  | [optional] 
**rating_group** | **str** |  | [optional] 
**revenue_recognition_rule_name** | **str** |  | [optional] 
**rev_rec_code** | **str** |  | [optional] 
**rev_rec_trigger_condition** | **str** |  | [optional] 
**segment** | **int** |  | [optional] 
**specific_billing_period** | **int** |  | [optional] 
**specific_end_date** | **date** |  | [optional] 
**taxable** | **bool** |  | [optional] 
**tax_code_name** | **str** |  | [optional] 
**tax_mode_option** | **str** |  | [optional] 
**t_cv** | **float** |  | [optional] 
**trigger_date** | **date** |  | [optional] 
**trigger_event** | **str** |  | [optional] 
**u_om** | **str** |  | [optional] 
**up_to_periods** | **int** |  | [optional] 
**up_to_periods_type** | **str** |  | [optional] 
**version** | **int** |  | [optional] 
**weekly_bill_cycle_day** | **str** |  | [optional] 
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**subscription_id** | **str** |  | [optional] 
**subscription_owner_id** | **str** |  | [optional] 
**invoice_owner_id** | **str** |  | [optional] 
**original_order_date** | **date** |  | [optional] 
**amended_by_order_on** | **date** |  | [optional] 
**validity_period_type** | **str** |  | [optional] 
**credit_option** | **str** |  | [optional] 
**apply_to_billing_period_partially** | **bool** |  | [optional] 
**product_charge_definition_id** | **str** |  | [optional] 
**reverted** | **bool** |  | [optional] 
**original_list_price** | **float** |  | [optional] 
**upsell_origin_charge_number** | **str** |  | [optional] 
**pricing_attributes** | **str** |  | [optional] 
**is_dimensional_price** | **bool** |  | [optional] 
**account_receivable_accounting_code_id** | **str** |  | [optional] 
**deferred_revenue_accounting_code_id** | **str** |  | [optional] 
**recognized_revenue_accounting_code_id** | **str** |  | [optional] 
**prepaid_uom** | **str** |  | [optional] 
**drawdown_uom** | **str** |  | [optional] 
**is_prorate_partial_month** | **bool** |  | [optional] 
**proration_unit** | **str** |  | [optional] 
**days_in_month** | **str** |  | [optional] 
**rate_plan** | [**ExpandedRatePlan**](ExpandedRatePlan.md) |  | [optional] 
**product_rate_plan_charge** | [**ExpandedProductRatePlanCharge**](ExpandedProductRatePlanCharge.md) |  | [optional] 
**rate_plan_charge_tiers** | [**List[ExpandedRatePlanChargeTier]**](ExpandedRatePlanChargeTier.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_rate_plan_charge import ExpandedRatePlanCharge

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedRatePlanCharge from a JSON string
expanded_rate_plan_charge_instance = ExpandedRatePlanCharge.from_json(json)
# print the JSON string representation of the object
print(ExpandedRatePlanCharge.to_json())

# convert the object into a dict
expanded_rate_plan_charge_dict = expanded_rate_plan_charge_instance.to_dict()
# create an instance of ExpandedRatePlanCharge from a dict
expanded_rate_plan_charge_from_dict = ExpandedRatePlanCharge.from_dict(expanded_rate_plan_charge_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


