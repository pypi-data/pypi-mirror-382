# ExpandedProductRatePlanCharge


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**accounting_code** | **str** |  | [optional] 
**apply_discount_to** | **str** |  | [optional] 
**bill_cycle_day** | **int** |  | [optional] 
**bill_cycle_type** | **str** |  | [optional] 
**billing_period** | **str** |  | [optional] 
**billing_period_alignment** | **str** |  | [optional] 
**billing_timing** | **str** |  | [optional] 
**charge_function** | **str** |  | [optional] 
**charge_model** | **str** |  | [optional] 
**charge_type** | **str** |  | [optional] 
**credit_option** | **str** |  | [optional] 
**default_quantity** | **float** |  | [optional] 
**deferred_revenue_account** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**discount_class_id** | **str** |  | [optional] 
**discount_level** | **str** |  | [optional] 
**drawdown_rate** | **float** |  | [optional] 
**end_date_condition** | **str** |  | [optional] 
**exclude_item_booking_from_revenue_accounting** | **bool** |  | [optional] 
**exclude_item_billing_from_revenue_accounting** | **bool** |  | [optional] 
**included_units** | **float** |  | [optional] 
**is_prepaid** | **bool** |  | [optional] 
**is_rollover** | **bool** |  | [optional] 
**is_stacked_discount** | **bool** |  | [optional] 
**legacy_revenue_reporting** | **bool** |  | [optional] 
**list_price_base** | **str** |  | [optional] 
**specific_list_price_base** | **int** |  | [optional] 
**max_quantity** | **float** |  | [optional] 
**min_quantity** | **float** |  | [optional] 
**name** | **str** |  | [optional] 
**number_of_period** | **int** |  | [optional] 
**overage_calculation_option** | **str** |  | [optional] 
**overage_unused_units_credit_option** | **str** |  | [optional] 
**prepaid_operation_type** | **str** |  | [optional] 
**proration_option** | **str** |  | [optional] 
**prepaid_quantity** | **float** |  | [optional] 
**prepaid_total_quantity** | **float** |  | [optional] 
**price_change_option** | **str** |  | [optional] 
**price_increase_percentage** | **float** |  | [optional] 
**product_rate_plan_charge_number** | **str** |  | [optional] 
**rating_group** | **str** |  | [optional] 
**recognized_revenue_account** | **str** |  | [optional] 
**revenue_recognition_rule_name** | **str** |  | [optional] 
**rev_rec_trigger_condition** | **str** |  | [optional] 
**rollover_apply** | **str** |  | [optional] 
**rollover_periods** | **int** |  | [optional] 
**rollover_period_length** | **int** |  | [optional] 
**smoothing_model** | **str** |  | [optional] 
**specific_billing_period** | **int** |  | [optional] 
**taxable** | **bool** |  | [optional] 
**tax_code** | **str** |  | [optional] 
**tax_mode** | **str** |  | [optional] 
**trigger_event** | **str** |  | [optional] 
**up_to_periods** | **int** |  | [optional] 
**up_to_periods_type** | **str** |  | [optional] 
**usage_record_rating_option** | **str** |  | [optional] 
**use_discount_specific_accounting_code** | **bool** |  | [optional] 
**use_tenant_default_for_price_change** | **bool** |  | [optional] 
**validity_period_type** | **str** |  | [optional] 
**weekly_bill_cycle_day** | **str** |  | [optional] 
**price_upsell_quantity_stacked** | **bool** |  | [optional] 
**delivery_schedule_id** | **str** |  | [optional] 
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**commitment_type** | **str** |  | [optional] 
**is_committed** | **bool** |  | [optional] 
**product_rate_plan_id** | **str** |  | [optional] 
**is_unbilled** | **bool** |  | [optional] 
**is_allocation_eligible** | **bool** |  | [optional] 
**product_category** | **str** |  | [optional] 
**product_class** | **str** |  | [optional] 
**product_family** | **str** |  | [optional] 
**product_line** | **str** |  | [optional] 
**revenue_recognition_timing** | **str** |  | [optional] 
**revenue_amortization_method** | **str** |  | [optional] 
**apply_to_billing_period_partially** | **bool** |  | [optional] 
**account_receivable_accounting_code_id** | **str** |  | [optional] 
**recognized_revenue_accounting_code_id** | **str** |  | [optional] 
**deferred_revenue_accounting_code_id** | **str** |  | [optional] 
**adjustment_liability_accounting_code_id** | **str** |  | [optional] 
**adjustment_revenue_accounting_code_id** | **str** |  | [optional] 
**contract_asset_accounting_code_id** | **str** |  | [optional] 
**contract_liability_accounting_code_id** | **str** |  | [optional] 
**contract_recognized_revenue_accounting_code_id** | **str** |  | [optional] 
**unbilled_receivables_accounting_code_id** | **str** |  | [optional] 
**rev_rec_code** | **str** |  | [optional] 
**u_om** | **str** |  | [optional] 
**drawdown_uom** | **str** |  | [optional] 
**prepaid_uom** | **str** |  | [optional] 
**product_rate_plan** | [**ExpandedProductRatePlan**](ExpandedProductRatePlan.md) |  | [optional] 
**product_rate_plan_charge_tiers** | [**List[ExpandedProductRatePlanChargeTier]**](ExpandedProductRatePlanChargeTier.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_product_rate_plan_charge import ExpandedProductRatePlanCharge

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedProductRatePlanCharge from a JSON string
expanded_product_rate_plan_charge_instance = ExpandedProductRatePlanCharge.from_json(json)
# print the JSON string representation of the object
print(ExpandedProductRatePlanCharge.to_json())

# convert the object into a dict
expanded_product_rate_plan_charge_dict = expanded_product_rate_plan_charge_instance.to_dict()
# create an instance of ExpandedProductRatePlanCharge from a dict
expanded_product_rate_plan_charge_from_dict = ExpandedProductRatePlanCharge.from_dict(expanded_product_rate_plan_charge_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


