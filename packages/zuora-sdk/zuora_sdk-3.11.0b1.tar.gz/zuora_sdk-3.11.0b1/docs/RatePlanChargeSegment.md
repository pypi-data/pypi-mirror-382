# RatePlanChargeSegment


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**amended_by_order_on** | **date** | The date when the rate plan charge is amended through an order or amendment. This field is to standardize the booking date information to increase audit ability and traceability of data between Zuora Billing and Zuora Revenue. It is mapped as the booking date for a sale order line in Zuora Revenue.  | [optional] 
**apply_discount_to** | [**ApplyDiscountTo**](ApplyDiscountTo.md) |  | [optional] 
**charge_function** | [**ChargeFunction**](ChargeFunction.md) |  | [optional] 
**charge_model_configuration** | [**ChargeModelConfigurationForSubscription**](ChargeModelConfigurationForSubscription.md) |  | [optional] 
**charged_through_date** | **date** | The date through which a customer has been billed for the charge.  | [optional] 
**commitment_type** | [**CommitmentType**](CommitmentType.md) |  | [optional] 
**prepaid_committed_amount** | **str** |  | [optional] 
**credit_option** | **str** | **Note**: This field is only available if you have the [Prepaid with Drawdown](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown) feature enabled.  To use this field, you must set the &#x60;X-Zuora-WSDL-Version&#x60; request header to 114 or higher. Otherwise, an error occurs.  The way to calculate credit. See [Credit Option](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown/Create_prepayment_charge#Credit_Option) for more information.  | [optional] 
**currency** | **str** | Currency used by the account. For example, &#x60;USD&#x60; or &#x60;EUR&#x60;. | [optional] 
**delivery_schedule** | [**DeliverySchedule**](DeliverySchedule.md) |  | [optional] 
**number_of_deliveries** | **float** |  | [optional] 
**description** | **str** | Description of the rate plan charge. | [optional] 
**discount_amount** | **float** | The amount of the discount. | [optional] 
**discount_apply_details** | [**List[DiscountApplyDetail]**](DiscountApplyDetail.md) | Container for the application details about a discount rate plan charge.   Only discount rate plan charges have values in this field.  | [optional] 
**discount_class** | **str** | The class that the discount belongs to. The discount class defines the order in which discount rate plan charges are applied.  For more information, see [Manage Discount Classes](https://knowledgecenter.zuora.com/BC_Subscription_Management/Product_Catalog/B_Charge_Models/Manage_Discount_Classes).  | [optional] 
**discount_level** | [**DiscountLevel**](DiscountLevel.md) |  | [optional] 
**discount_percentage** | **float** | The amount of the discount as a percentage.  | [optional] 
**apply_to_billing_period_partially** | **bool** |  | [optional] 
**dmrc** | **float** | The change (delta) of monthly recurring charge exists when the change in monthly recurring revenue caused by an amendment or a new subscription.  | [optional] 
**done** | **bool** | A value of &#x60;true&#x60; indicates that an invoice for a charge segment has been completed. A value of &#x60;false&#x60; indicates that an invoice has not been completed for the charge segment.  | [optional] 
**drawdown_rate** | **float** |  | [optional] 
**drawdown_uom** | **str** | Specifies the units to measure usage. | [optional] 
**dtcv** | **float** | After an amendment or an AutomatedPriceChange event, &#x60;dtcv&#x60; displays the change (delta) for the total contract value (TCV) amount for this charge, compared with its previous value with recurring charge types.  | [optional] 
**effective_end_date** | **date** |  | [optional] 
**effective_start_date** | **date** |  | [optional] 
**end_date_condition** | [**EndDateCondition**](EndDateCondition.md) |  | [optional] 
**included_units** | **float** |  | [optional] 
**input_argument_id** | **str** |  | [optional] 
**is_committed** | **bool** |  | [optional] 
**is_prepaid** | **bool** |  | [optional] 
**is_rollover** | **bool** |  | [optional] 
**mrr** | **float** |  | [optional] 
**original_order_date** | **date** |  | [optional] 
**overage_price** | **float** |  | [optional] 
**prepaid_operation_type** | **str** |  | [optional] 
**prepaid_quantity** | **float** |  | [optional] 
**prepaid_total_quantity** | **float** |  | [optional] 
**prepaid_uom** | **str** | Specifies the units to measure usage. | [optional] 
**quantity** | **float** |  | [optional] 
**price** | **float** |  | [optional] 
**price_change_option** | [**PriceChangeOption**](PriceChangeOption.md) |  | [optional] [default to PriceChangeOption.NOCHANGE]
**price_increase_percentage** | **float** |  | [optional] 
**pricing_summary** | **str** |  | [optional] 
**original_list_price** | **float** |  | [optional] 
**processed_through_date** | **date** |  | [optional] 
**rollover_apply** | **str** |  | [optional] 
**rollover_period_length** | **int** |  | [optional] 
**rollover_periods** | **int** |  | [optional] 
**proration_option** | **str** |  | [optional] 
**segment** | **int** |  | [optional] 
**specific_end_date** | **date** |  | [optional] 
**subscription_charge_interval_pricing** | [**List[IntervalPricing]**](IntervalPricing.md) |  | [optional] 
**tcv** | **float** |  | [optional] 
**tiers** | [**List[RatePlanChargeTier]**](RatePlanChargeTier.md) |  | [optional] 
**trigger_date** | **date** |  | [optional] 
**billing_period_alignment** | [**BillingPeriodAlignment**](BillingPeriodAlignment.md) |  | [optional] 
**trigger_event** | [**TriggerEvent**](TriggerEvent.md) |  | [optional] 
**up_to_periods** | **int** |  | [optional] 
**up_to_periods_type** | [**UpToPeriodsType**](UpToPeriodsType.md) |  | [optional] 
**validity_period_type** | [**ValidityPeriodType**](ValidityPeriodType.md) |  | [optional] 
**sales_price** | **float** |  | [optional] 
**accounting_code** | **str** |  | [optional] 
**revenue_recognition_code** | **str** |  | [optional] 
**rev_rec_trigger_condition** | **str** |  | [optional] 
**estimated_end_date** | **date** |  | [optional] 
**estimated_start_date** | **date** |  | [optional] 
**taxable** | **bool** |  | [optional] 
**tax_code** | **str** |  | [optional] 
**tax_mode** | **str** |  | [optional] 
**pricing_attributes** | **Dict[str, object]** | Container for pricing attributes used in dynamic pricing.  **Note**: This field is only available when DynamicPricing permission enabled.  | [optional] 
**is_dimensional_price** | **bool** | Indicates whether the charge uses dimensional pricing.  **Note**: This field is only available when DynamicPricing permission enabled.  | [optional] 
**is_price_negotiated** | **bool** | Indicates whether the charge uses negotiated pricing.  **Note**: This field is only available when NegotiatedPriceTable permission enabled.  | [optional] 

## Example

```python
from zuora_sdk.models.rate_plan_charge_segment import RatePlanChargeSegment

# TODO update the JSON string below
json = "{}"
# create an instance of RatePlanChargeSegment from a JSON string
rate_plan_charge_segment_instance = RatePlanChargeSegment.from_json(json)
# print the JSON string representation of the object
print(RatePlanChargeSegment.to_json())

# convert the object into a dict
rate_plan_charge_segment_dict = rate_plan_charge_segment_instance.to_dict()
# create an instance of RatePlanChargeSegment from a dict
rate_plan_charge_segment_from_dict = RatePlanChargeSegment.from_dict(rate_plan_charge_segment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


