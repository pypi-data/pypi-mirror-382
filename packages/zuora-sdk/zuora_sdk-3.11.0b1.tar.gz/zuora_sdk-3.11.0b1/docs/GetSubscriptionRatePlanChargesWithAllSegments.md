# GetSubscriptionRatePlanChargesWithAllSegments


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**billing_day** | **str** |  | [optional] 
**billing_period** | [**BillingPeriod**](BillingPeriod.md) |  | [optional] 
**billing_period_alignment** | [**BillingPeriodAlignment**](BillingPeriodAlignment.md) |  | [optional] 
**billing_timing** | [**BillingTiming**](BillingTiming.md) |  | [optional] 
**charge_segments** | [**List[RatePlanChargeSegment]**](RatePlanChargeSegment.md) | Billing cycle day (BCD), which is when bill runs generate invoices for charges associated with the product rate plan charge or the account.    Values:  * &#x60;DefaultFromCustomer&#x60; * &#x60;SpecificDayofMonth(# of the month)&#x60; * &#x60;SubscriptionStartDay&#x60; * &#x60;ChargeTriggerDay&#x60; * &#x60;SpecificDayofWeek/dayofweek&#x60;: in which dayofweek is the day in the week you define your billing periods to start.  In the response data, a day-of-the-month ordinal value (&#x60;first&#x60;-&#x60;31st&#x60;) appears in place of the hash sign above (\&quot;#\&quot;). If this value exceeds the number of days in a particular month, the last day of the month is used as the BCD.  | [optional] 
**exclude_item_billing_from_revenue_accounting** | **bool** |  | [optional] 
**exclude_item_booking_from_revenue_accounting** | **bool** |  | [optional] 
**invoice_schedule_id** | **str** |  | [optional] 
**is_allocation_eligible** | **bool** |  | [optional] 
**is_unbilled** | **bool** |  | [optional] 
**list_price_base** | [**ChargeListPriceBase**](ChargeListPriceBase.md) |  | [optional] 
**model** | [**ChargeModel**](ChargeModel.md) |  | [optional] 
**name** | **str** |  | [optional] 
**number** | **str** |  | [optional] 
**number_of_periods** | **int** |  | [optional] 
**original_charge_id** | **str** |  | [optional] 
**overage_calculation_option** | [**OverageCalculationOption**](OverageCalculationOption.md) |  | [optional] 
**overage_unused_units_credit_option** | [**OverageUnusedUnitsCreditOption**](OverageUnusedUnitsCreditOption.md) |  | [optional] 
**product_category** | **str** |  | [optional] 
**product_class** | **str** |  | [optional] 
**product_family** | **str** |  | [optional] 
**product_line** | **str** |  | [optional] 
**product_rate_plan_charge_id** | **str** |  | [optional] 
**product_rate_plan_charge_number** | **str** |  | [optional] 
**rating_group** | [**RatingGroup**](RatingGroup.md) |  | [optional] 
**smoothing_model** | [**SmoothingModel**](SmoothingModel.md) |  | [optional] 
**specific_billing_period** | **int** |  | [optional] 
**specific_list_price_base** | **int** |  | [optional] 
**type** | [**ChargeType**](ChargeType.md) |  | [optional] 
**unused_units_credit_rates** | **float** |  | [optional] 
**uom** | **str** | Specifies the units to measure usage. | [optional] 
**usage_record_rating_option** | [**UsageRecordRatingOption**](UsageRecordRatingOption.md) |  | [optional] 
**version** | **int** |  | [optional] 
**amended_by_order_on** | **date** | The date when the rate plan charge is amended through an order or amendment. This field is to standardize the booking date information to increase audit ability and traceability of data between Zuora Billing and Zuora Revenue. It is mapped as the booking date for a sale order line in Zuora Revenue.  | [optional] 
**apply_discount_to** | [**ApplyDiscountTo**](ApplyDiscountTo.md) |  | [optional] 
**charge_function** | [**ChargeFunction**](ChargeFunction.md) |  | [optional] 
**charge_model_configuration** | [**ChargeModelConfigurationForSubscription**](ChargeModelConfigurationForSubscription.md) |  | [optional] 
**charged_through_date** | **date** | The date through which a customer has been billed for the charge.  | [optional] 
**commitment_type** | [**CommitmentType**](CommitmentType.md) |  | [optional] 
**prepaid_committed_amount** | **str** |  | [optional] 
**product_charge_definition_id** | **str** |  | [optional] 
**is_stacked_discount** | **bool** |  | [optional] 
**reflect_discount_in_net_amount** | **bool** |  | [optional] 
**centralized_price** | **bool** |  | [optional] 
**number_of_deliveries** | **float** |  | [optional] 
**credit_option** | **str** | **Note**: This field is only available if you have the [Prepaid with Drawdown](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown) feature enabled.  To use this field, you must set the &#x60;X-Zuora-WSDL-Version&#x60; request header to 114 or higher. Otherwise, an error occurs.  The way to calculate credit. See [Credit Option](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown/Create_prepayment_charge#Credit_Option) for more information.  | [optional] 
**currency** | **str** | Currency used by the account. For example, &#x60;USD&#x60; or &#x60;EUR&#x60;. | [optional] 
**delivery_schedule** | [**DeliverySchedule**](DeliverySchedule.md) |  | [optional] 
**description** | **str** | Description of the rate plan charge. | [optional] 
**discount_amount** | **float** | The amount of the discount. | [optional] 
**discount_apply_details** | [**List[DiscountApplyDetail]**](DiscountApplyDetail.md) | Container for the application details about a discount rate plan charge.   Only discount rate plan charges have values in this field.  | [optional] 
**discount_class** | **str** | The class that the discount belongs to. The discount class defines the order in which discount rate plan charges are applied.  For more information, see [Manage Discount Classes](https://knowledgecenter.zuora.com/BC_Subscription_Management/Product_Catalog/B_Charge_Models/Manage_Discount_Classes).  | [optional] 
**discount_level** | [**DiscountLevel**](DiscountLevel.md) |  | [optional] 
**discount_percentage** | **float** | The amount of the discount as a percentage.  | [optional] 
**apply_to_billing_period_partially** | **bool** | Allow the discount duration to be aligned with the billing period partially. **Note**: This field is only available if you have the Enhanced Discounts feature enabled.  | [optional] 
**dmrc** | **str** | The change (delta) of monthly recurring charge exists when the change in monthly recurring revenue caused by an amendment or a new subscription.  | [optional] 
**done** | **bool** | A value of &#x60;true&#x60; indicates that an invoice for a charge segment has been completed. A value of &#x60;false&#x60; indicates that an invoice has not been completed for the charge segment.  | [optional] 
**drawdown_rate** | **str** |  | [optional] 
**drawdown_uom** | **str** | Specifies the units to measure usage. | [optional] 
**dtcv** | **str** | After an amendment or an AutomatedPriceChange event, &#x60;dtcv&#x60; displays the change (delta) for the total contract value (TCV) amount for this charge, compared with its previous value with recurring charge types.  | [optional] 
**effective_end_date** | **date** |  | [optional] 
**effective_start_date** | **date** |  | [optional] 
**end_date_condition** | [**EndDateCondition**](EndDateCondition.md) |  | [optional] 
**id** | **str** |  | [optional] 
**included_units** | **float** |  | [optional] 
**overage_price** | **float** |  | [optional] 
**input_argument_id** | **str** |  | [optional] 
**is_committed** | **bool** |  | [optional] 
**is_prepaid** | **bool** |  | [optional] 
**is_rollover** | **bool** |  | [optional] 
**mrr** | **str** |  | [optional] 
**original_order_date** | **date** |  | [optional] 
**prepaid_operation_type** | **str** |  | [optional] 
**prepaid_quantity** | **str** |  | [optional] 
**prepaid_total_quantity** | **str** |  | [optional] 
**prepaid_uom** | **str** | Specifies the units to measure usage. | [optional] 
**quantity** | **float** |  | [optional] 
**price** | **float** |  | [optional] 
**original_list_price** | **float** |  | [optional] 
**price_change_option** | [**PriceChangeOption**](PriceChangeOption.md) |  | [optional] [default to PriceChangeOption.NOCHANGE]
**price_increase_percentage** | **float** |  | [optional] 
**pricing_summary** | **str** |  | [optional] 
**processed_through_date** | **date** |  | [optional] 
**rollover_apply** | **str** |  | [optional] 
**rollover_period_length** | **int** |  | [optional] 
**rollover_periods** | **int** |  | [optional] 
**proration_option** | **str** |  | [optional] 
**segment** | **int** |  | [optional] 
**specific_end_date** | **date** |  | [optional] 
**subscription_charge_interval_pricing** | [**List[IntervalPricing]**](IntervalPricing.md) |  | [optional] 
**tcv** | **str** |  | [optional] 
**tiers** | [**List[RatePlanChargeTier]**](RatePlanChargeTier.md) |  | [optional] 
**trigger_date** | **date** |  | [optional] 
**trigger_event** | [**TriggerEvent**](TriggerEvent.md) |  | [optional] 
**upsell_origin_charge_number** | **str** | **Note**: The Quantity Upsell feature is in Limited Availability. If you wish to have access to the feature, submit a request at [Zuora Global Support](https://support.zuora.com).  The identifier of the original upselling charge associated with the current charge.  | [optional] 
**up_to_periods** | **int** |  | [optional] 
**up_to_periods_type** | [**UpToPeriodsType**](UpToPeriodsType.md) |  | [optional] 
**validity_period_type** | [**ValidityPeriodType**](ValidityPeriodType.md) |  | [optional] 
**price_upsell_quantity_stacked** | **bool** | This field is availabe when PriceUpsellQuantityStacked permission enabled | [optional] 
**pob_policy** | **str** | The POB policy type, it is available when permission EnableAdditionalRevenueFields is on  | [optional] 
**sales_price** | **float** |  | [optional] 
**estimated_end_date** | **date** |  | [optional] 
**estimated_start_date** | **date** |  | [optional] 
**taxable** | **bool** |  | [optional] 
**tax_code** | **str** |  | [optional] 
**tax_mode** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.get_subscription_rate_plan_charges_with_all_segments import GetSubscriptionRatePlanChargesWithAllSegments

# TODO update the JSON string below
json = "{}"
# create an instance of GetSubscriptionRatePlanChargesWithAllSegments from a JSON string
get_subscription_rate_plan_charges_with_all_segments_instance = GetSubscriptionRatePlanChargesWithAllSegments.from_json(json)
# print the JSON string representation of the object
print(GetSubscriptionRatePlanChargesWithAllSegments.to_json())

# convert the object into a dict
get_subscription_rate_plan_charges_with_all_segments_dict = get_subscription_rate_plan_charges_with_all_segments_instance.to_dict()
# create an instance of GetSubscriptionRatePlanChargesWithAllSegments from a dict
get_subscription_rate_plan_charges_with_all_segments_from_dict = GetSubscriptionRatePlanChargesWithAllSegments.from_dict(get_subscription_rate_plan_charges_with_all_segments_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


