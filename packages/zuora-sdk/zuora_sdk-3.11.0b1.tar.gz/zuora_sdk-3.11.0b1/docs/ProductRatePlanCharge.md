# ProductRatePlanCharge


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**class__ns** | **str** | Class associated with the corresponding item in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**deferred_rev_account__ns** | **str** | Deferrred revenue account associated with the corresponding item in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**department__ns** | **str** | Department associated with the corresponding item in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**include_children__ns** | [**ProductRatePlanChargeObjectNSFieldsIncludeChildrenNS**](ProductRatePlanChargeObjectNSFieldsIncludeChildrenNS.md) |  | [optional] 
**integration_id__ns** | **str** | ID of the corresponding object in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**integration_status__ns** | **str** | Status of the product rate plan charge&#39;s synchronization with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**item_type__ns** | [**ProductRatePlanChargeObjectNSFieldsItemTypeNS**](ProductRatePlanChargeObjectNSFieldsItemTypeNS.md) |  | [optional] 
**location__ns** | **str** | Location associated with the corresponding item in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**recognized_rev_account__ns** | **str** | Recognized revenue account associated with the corresponding item in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**rev_rec_end__ns** | [**ProductRatePlanChargeObjectNSFieldsRevRecEndNS**](ProductRatePlanChargeObjectNSFieldsRevRecEndNS.md) |  | [optional] 
**rev_rec_start__ns** | [**ProductRatePlanChargeObjectNSFieldsRevRecStartNS**](ProductRatePlanChargeObjectNSFieldsRevRecStartNS.md) |  | [optional] 
**rev_rec_template_type__ns** | **str** | Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**subsidiary__ns** | **str** | Subsidiary associated with the corresponding item in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**sync_date__ns** | **str** | Date when the product rate plan charge was synchronized with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**id** | **str** | Object identifier. | [optional] 
**product_rate_plan_id** | **str** | The ID of the product rate plan associated with this product rate plan charge. | [optional] 
**accounting_code** | **str** | The accounting code for the charge. Accounting codes group transactions that contain similar accounting attributes. | [optional] 
**apply_discount_to** | [**ApplyDiscountTo**](ApplyDiscountTo.md) |  | [optional] 
**bill_cycle_day** | **int** | Sets the bill cycle day (BCD) for the charge. The BCD determines which day of the month customer is billed. The BCD value in the account can override the BCD in this object.  StackedDiscount **Character limit**: 2   **Values**: a valid BCD integer, 1 - 31 | [optional] 
**bill_cycle_type** | [**BillCycleType**](BillCycleType.md) |  | [optional] 
**billing_period** | [**BillingPeriodProductRatePlanChargeRest**](BillingPeriodProductRatePlanChargeRest.md) |  | [optional] 
**billing_period_alignment** | [**BillingPeriodAlignmentProductRatePlanChargeRest**](BillingPeriodAlignmentProductRatePlanChargeRest.md) |  | [optional] 
**billing_timing** | [**BillingTimingProductRatePlanChargeRest**](BillingTimingProductRatePlanChargeRest.md) |  | [optional] 
**charge_function** | [**ChargeFunction**](ChargeFunction.md) |  | [optional] 
**charge_model** | [**ChargeModelProductRatePlanChargeRest**](ChargeModelProductRatePlanChargeRest.md) |  | [optional] 
**charge_model_configuration** | [**ChargeModelConfiguration**](ChargeModelConfiguration.md) |  | [optional] 
**charge_type** | [**ChargeType**](ChargeType.md) |  | [optional] 
**commitment_type** | [**CommitmentType**](CommitmentType.md) |  | [optional] 
**created_by_id** | **str** | The automatically generated ID of the Zuora user who created the &#x60;ProductRatePlanCharge&#x60; object. | [optional] 
**created_date** | **datetime** | The date when the &#x60;ProductRatePlanCharge&#x60; object was created.  | [optional] 
**default_quantity** | **float** | The default quantity of units, such as the number of authors in a hosted wiki service. This field is required if you use a per-unit pricing model.   **Character limit**: 16   **Values**: a valid quantity value.   **Note**: When &#x60;ChargeModel&#x60; is &#x60;Tiered Pricing&#x60; or &#x60;Volume Pricing&#x60;, if this field is not specified, the value will default to &#x60;0&#x60;. | [optional] 
**deferred_revenue_account** | **str** | The name of the deferred revenue account for this charge.   This feature is in **Limited Availability**. If you wish to have access to the feature, submit a request at [Zuora Global Support](http://support.zuora.com/).  | [optional] 
**delivery_schedule** | [**DeliveryScheduleProductRatePlanCharge**](DeliveryScheduleProductRatePlanCharge.md) |  | [optional] 
**description** | **str** | A description of the charge.  | [optional] 
**discount_level** | [**DiscountLevel**](DiscountLevel.md) |  | [optional] 
**drawdown_rate** | **float** | **Note**: This field is only available if you have the [Prepaid with Drawdown](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown) feature enabled.   The [conversion rate](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown/Create_drawdown_charge#UOM_Conversion) between Usage UOM and Drawdown UOM for a [drawdown charge](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown/Create_drawdown_charge). Must be a positive number (&gt;0). | [optional] 
**drawdown_uom** | **str** | **Note**: This field is only available if you have the [Prepaid with Drawdown](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown) feature enabled.  Unit of measurement for a [drawdown charge](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown/Create_drawdown_charge). | [optional] 
**end_date_condition** | [**EndDateConditionProductRatePlanChargeRest**](EndDateConditionProductRatePlanChargeRest.md) |  | [optional] [default to EndDateConditionProductRatePlanChargeRest.SUBSCRIPTIONEND]
**exclude_item_billing_from_revenue_accounting** | **bool** | The flag to exclude the related invoice items, invoice item adjustments, credit memo items, and debit memo items from revenue accounting.   **Notes**:    - To use this field, you must set the &#x60;X-Zuora-WSDL-Version&#x60; request header to &#x60;115&#x60; or later. Otherwise, an error occurs.   - This field is only available if you have the Billing - Revenue Integration feature enabled.  | [optional] 
**exclude_item_booking_from_revenue_accounting** | **bool** | The flag to exclude the related rate plan charges and order line items from revenue accounting.   **Notes**:    - To use this field, you must set the &#x60;X-Zuora-WSDL-Version&#x60; request header to &#x60;115&#x60; or later. Otherwise, an error occurs.   - This field is only available if you have the Billing - Revenue Integration feature enabled.  | [optional] 
**included_units** | **float** | Specifies the number of units in the base set of units.  **Character limit**: 16  **Values**: a positive decimal value  | [optional] 
**is_prepaid** | **bool** | **Note**: This field is only available if you have the [Prepaid with Drawdown](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown) feature enabled.   Indicates whether this charge is a prepayment (topup) charge or a drawdown charge. Values: &#x60;true&#x60; or &#x60;false&#x60;. | [optional] 
**is_rollover** | **bool** | **Note**: This field is only available if you have the [Prepaid with Drawdown](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown) feature enabled.   To use this field, you must set the &#x60;X-Zuora-WSDL-Version&#x60; request header to 114 or higher. Otherwise, an error occurs.   The value is either \&quot;True\&quot; or \&quot;False\&quot;. It determines whether the rollover fields are needed. | [optional] 
**is_stacked_discount** | **bool** | **Note**: This field is only applicable to the Discount - Percentage charge model.  To use this field, you must set the &#x60;X-Zuora-WSDL-Version&#x60; request header to 130 or higher. Otherwise, an error occurs.  This field indicates whether the discount is to be calculated as stacked discount. Possible values are as follows:  - &#x60;true&#x60;: This is a stacked discount, which should be calculated by stacking with other discounts.  - &#x60;false&#x60;: This is not a stacked discount, which should be calculated in sequence with other discounts.  For more information, see [Stacked discounts](https://knowledgecenter.zuora.com/Zuora_Billing/Products/Product_Catalog/B_Charge_Models/B_Discount_Charge_Models). | [optional] 
**is_unbilled** | **bool** | This field is used to dictate how to perform the accounting during revenue recognition.  **Note**: This feature is in the **Early Adopter** phase. If you want to use the feature, submit a request at &lt;a href&#x3D;\&quot;https://support.zuora.com/\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Zuora Global Support&lt;/a&gt;, and we will evaluate whether the feature is suitable for your use cases. | [optional] 
**revenue_recognition_timing** | **str** | This field is used to dictate the type of revenue recognition timing. | [optional] 
**revenue_amortization_method** | **str** | This field is used to dictate the type of revenue amortization method. | [optional] 
**legacy_revenue_reporting** | **bool** |  | [optional] 
**list_price_base** | [**ListPriceBase**](ListPriceBase.md) |  | [optional] 
**min_quantity** | **float** | Specifies the minimum number of units for this charge. Use this field and the &#x60;MaxQuantity&#x60; field to create a range of units allowed in a product rate plan charge.   **Character limit**: 16   **Values**: a positive decimal value | [optional] 
**max_quantity** | **float** | Specifies the maximum number of units for this charge. Use this field and the &#x60;MinQuantity&#x60; field to create a range of units allowed in a product rate plan charge.   **Character limit**: 16   **Values**: a positive decimal value | [optional] 
**name** | **str** | The name of the product rate plan charge.  | [optional] 
**number_of_period** | **int** | Specifies the number of periods to use when calculating charges in an overage smoothing charge model. The valid value is a positive whole number. | [optional] 
**overage_calculation_option** | [**OverageCalculationOption**](OverageCalculationOption.md) |  | [optional] 
**overage_unused_units_credit_option** | [**OverageUnusedUnitsCreditOption**](OverageUnusedUnitsCreditOption.md) |  | [optional] 
**prepaid_operation_type** | [**PrepaidOperationType**](PrepaidOperationType.md) |  | [optional] 
**prepaid_quantity** | **float** | **Note**: This field is only available if you have the [Prepaid with Drawdown](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown) feature enabled.  The number of units included in a [prepayment charge](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown/Create_prepayment_charge). Must be a positive number (&gt;0). | [optional] 
**prepaid_total_quantity** | **float** | **Note**: This field is only available if you have the [Prepaid with Drawdown](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown) feature enabled.  The total amount of units that end customers can use during a validity period when they subscribe to a [prepayment charge](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown/Create_prepayment_charge). | [optional] 
**prepaid_uom** | **str** | **Note**: This field is only available if you have the [Prepaid with Drawdown](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown) feature enabled. Unit of measurement for a [prepayment charge](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown/Create_prepayment_charge). | [optional] 
**prepay_periods** | **int** | The number of periods to which prepayment is set. **Note:** This field is only available if you already have the prepayment feature enabled.  The prepayment feature is deprecated and available only for backward compatibility. Zuora does not support enabling this feature anymore. | [optional] 
**price_change_option** | [**PriceChangeOption**](PriceChangeOption.md) |  | [optional] [default to PriceChangeOption.NOCHANGE]
**price_increase_percentage** | **float** | Specifies the percentage to increase or decrease the price of a termed subscription&#39;s renewal. Use this field if you set the value to &#x60;SpecificPercentageValue&#x60;.   **Character limit**: 16   **Values**: a decimal value between -100 and 100 | [optional] 
**price_increase_option** | [**PriceIncreaseOption**](PriceIncreaseOption.md) |  | [optional] 
**rating_group** | [**RatingGroup**](RatingGroup.md) |  | [optional] 
**recognized_revenue_account** | **str** | The name of the recognized revenue account for this charge.   - Required when the Allow Blank Accounting Code setting is No.   - Optional when the Allow Blank Accounting Code setting is Yes.  This feature is in **Limited Availability**. If you wish to have access to the feature, submit a request at [Zuora Global Support](http://support.zuora.com/).  | [optional] 
**rev_rec_code** | **str** | Associates this product rate plan charge with a specific revenue recognition code. | [optional] 
**rev_rec_trigger_condition** | [**RevRecTriggerConditionProductRatePlanChargeRest**](RevRecTriggerConditionProductRatePlanChargeRest.md) |  | [optional] 
**revenue_recognition_rule_name** | [**RevenueRecognitionRuleName**](RevenueRecognitionRuleName.md) |  | [optional] 
**rollover_apply** | [**RolloverApply**](RolloverApply.md) |  | [optional] 
**rollover_periods** | **float** | **Note**: This field is only available if you have the [Prepaid with Drawdown](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/J_Billing_Operations/Prepaid_with_Drawdown) feature enabled.  To use this field, you must set the &#x60;X-Zuora-WSDL-Version&#x60; request header to 114 or higher. Otherwise, an error occurs.  This field defines the number of rollover periods, it is restricted to 3. | [optional] 
**smoothing_model** | [**SmoothingModel**](SmoothingModel.md) |  | [optional] 
**specific_billing_period** | **int** | Customizes the number of months or weeks for the charges billing period. This field is required if you set the value of the BillingPeriod field to &#x60;Specific Months&#x60; or &#x60;Specific Weeks&#x60;.  The valid value is a positive integer. | [optional] 
**specific_list_price_base** | **object** | The number of months for the list price base of the charge. The value of this field is &#x60;null&#x60; if you do not set the value of the &#x60;ListPriceBase&#x60; field to &#x60;Per Specific Months&#x60;.   **Notes**:    - This field is available only if you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Billing/Subscriptions/Product_Catalog/I_Annual_List_Price\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Annual List Price&lt;/a&gt; feature enabled.   - To use this field, you must set the &#x60;X-Zuora-WSDL-Version&#x60; request header to &#x60;129&#x60; or later. Otherwise, an error occurs.   - The value of this field is &#x60;null&#x60; if you do not set the value of the &#x60;ListPriceBase&#x60; field to &#x60;Per Specific Months&#x60;. | [optional] 
**tax_code** | **str** | Specifies the tax code for taxation rules. Required when the Taxable field is set to &#x60;True&#x60;.   **Note**: This value affects the tax calculation of rate plan charges that come from the &#x60;ProductRatePlanCharge&#x60;. | [optional] 
**tax_mode** | [**TaxMode**](TaxMode.md) |  | [optional] 
**taxable** | **bool** | Determines whether the charge is taxable. When set to &#x60;True&#x60;, the TaxMode and TaxCode fields are required when creating or updating th ProductRatePlanCharge object.   **Character limit**: 5   **Values**: &#x60;True&#x60;, &#x60;False&#x60;   **Note**: This value affects the tax calculation of rate plan charges that come from the &#x60;ProductRatePlanCharge&#x60;. | [optional] 
**trigger_event** | [**TriggerEventProductRatePlanChargeRest**](TriggerEventProductRatePlanChargeRest.md) |  | [optional] 
**uom** | **str** | Specifies the units to measure usage.    **Note**: You must specify this field when creating the following charge models:   - Per Unit Pricing   - Volume Pricin   - Overage Pricing   - Tiered Pricing   - Tiered with Overage Pricing | [optional] 
**up_to_periods** | **int** | Specifies the length of the period during which the charge is active. If this period ends before the subscription ends, the charge ends when this period ends.   **Character limit**: 5   **Values**: a whole number between 0 and 65535, exclusive   **Notes**:   - You must use this field together with the &#x60;UpToPeriodsType&#x60; field to specify the time period. This field is applicable only when the &#x60;EndDateCondition&#x60; field is set to &#x60;FixedPeriod&#x60;.    - If the subscription end date is subsequently changed through a Renewal, or Terms and Conditions amendment, the charge end date will change accordingly up to the original period end. | [optional] 
**up_to_periods_type** | [**UpToPeriodsTypeProductRatePlanChargeRest**](UpToPeriodsTypeProductRatePlanChargeRest.md) |  | [optional] [default to UpToPeriodsTypeProductRatePlanChargeRest.BILLING_PERIODS]
**updated_by_id** | **str** | The ID of the last user to update the object.  | [optional] 
**updated_date** | **datetime** | The date when the object was last updated.  | [optional] 
**usage_record_rating_option** | [**UsageRecordRatingOption**](UsageRecordRatingOption.md) |  | [optional] 
**use_discount_specific_accounting_code** | **bool** | Determines whether to define a new accounting code for the new discount charge.   **Character limit**: 5   **Values**: &#x60;True&#x60;, &#x60;False&#x60; | [optional] 
**use_tenant_default_for_price_change** | **bool** | Applies the tenant-level percentage uplift value for an automatic price change to a termed subscription&#39;s renewal.    **Character limit**: 5   **Values**: &#x60;true&#x60;, &#x60;false&#x60; | [optional] 
**validity_period_type** | [**ValidityPeriodType**](ValidityPeriodType.md) |  | [optional] 
**weekly_bill_cycle_day** | [**WeeklyBillCycleDay**](WeeklyBillCycleDay.md) |  | [optional] 
**rating_groups_operator_type** | [**RatingGroupsOperatorType**](RatingGroupsOperatorType.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.product_rate_plan_charge import ProductRatePlanCharge

# TODO update the JSON string below
json = "{}"
# create an instance of ProductRatePlanCharge from a JSON string
product_rate_plan_charge_instance = ProductRatePlanCharge.from_json(json)
# print the JSON string representation of the object
print(ProductRatePlanCharge.to_json())

# convert the object into a dict
product_rate_plan_charge_dict = product_rate_plan_charge_instance.to_dict()
# create an instance of ProductRatePlanCharge from a dict
product_rate_plan_charge_from_dict = ProductRatePlanCharge.from_dict(product_rate_plan_charge_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


