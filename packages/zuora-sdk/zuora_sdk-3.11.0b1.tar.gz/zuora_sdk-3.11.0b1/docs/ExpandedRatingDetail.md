# ExpandedRatingDetail


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**charge_type** | **str** |  | [optional] 
**charge_model** | **str** |  | [optional] 
**formula** | **str** |  | [optional] 
**calculation** | **str** |  | [optional] 
**calculated_amount** | **float** |  | [optional] 
**currency** | **str** |  | [optional] 
**unit_of_measure** | **str** |  | [optional] 
**billed_quantity** | **float** |  | [optional] 
**billed_amount** | **float** |  | [optional] 
**quantity** | **float** |  | [optional] 
**is_proration** | **bool** |  | [optional] 
**is_credit** | **bool** |  | [optional] 
**list_price_base** | **str** |  | [optional] 
**billing_cycle_day** | **int** |  | [optional] 
**billing_cycle_type** | **str** |  | [optional] 
**billing_period** | **str** |  | [optional] 
**specific_billing_period** | **str** |  | [optional] 
**validity_period_type** | **str** |  | [optional] 
**billing_period_alignment** | **str** |  | [optional] 
**alignment_start_date** | **date** |  | [optional] 
**amount_without_tax** | **float** |  | [optional] 
**is_inclusive_tax_no_rounding** | **bool** |  | [optional] 
**is_proration_partial_period** | **bool** |  | [optional] 
**is_prorate_monthly_charges** | **bool** |  | [optional] 
**is_prorate_weekly_charges** | **bool** |  | [optional] 
**proration_unit_rule** | **str** |  | [optional] 
**days_in_month_rule** | **str** |  | [optional] 
**recurring_credit_proration_option_rule** | **str** |  | [optional] 
**is_credit_with_original_ce** | **bool** |  | [optional] 
**is_prorate_discount_credit** | **bool** |  | [optional] 
**stacked_discount_class_apply_rule** | **str** |  | [optional] 
**recurring_period_start** | **date** |  | [optional] 
**recurring_period_end** | **date** |  | [optional] 
**charge_start_date** | **date** |  | [optional] 
**charge_end_date** | **date** |  | [optional] 
**sub_start_date** | **date** |  | [optional] 
**sub_end_date** | **date** |  | [optional] 
**term_start_date** | **date** |  | [optional] 
**term_end_date** | **date** |  | [optional] 
**credit_option** | **str** |  | [optional] 
**funding_price** | **float** |  | [optional] 
**total_balance** | **float** |  | [optional] 
**remaining_balance** | **float** |  | [optional] 
**original_billing_period_start** | **date** |  | [optional] 
**original_billing_period_end** | **date** |  | [optional] 
**original_amount** | **float** |  | [optional] 
**base_price** | **str** |  | [optional] 
**discount_class** | **str** |  | [optional] 
**discount_class_order** | **int** |  | [optional] 
**discount_level** | **str** |  | [optional] 
**discount_apply_sequence** | **int** |  | [optional] 
**discount_schedule_period_start** | **date** |  | [optional] 
**discount_schedule_period_end** | **date** |  | [optional] 
**regular_charge_amount** | **float** |  | [optional] 
**regular_charge_amount_left** | **float** |  | [optional] 
**original_regular_charge_amount** | **float** |  | [optional] 
**discount_balance_formula** | **str** |  | [optional] 
**invoice_item_id** | **str** |  | [optional] 
**credit_memo_item_id** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_rating_detail import ExpandedRatingDetail

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedRatingDetail from a JSON string
expanded_rating_detail_instance = ExpandedRatingDetail.from_json(json)
# print the JSON string representation of the object
print(ExpandedRatingDetail.to_json())

# convert the object into a dict
expanded_rating_detail_dict = expanded_rating_detail_instance.to_dict()
# create an instance of ExpandedRatingDetail from a dict
expanded_rating_detail_from_dict = ExpandedRatingDetail.from_dict(expanded_rating_detail_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


