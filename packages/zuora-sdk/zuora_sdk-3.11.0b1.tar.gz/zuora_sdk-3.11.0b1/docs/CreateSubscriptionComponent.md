# CreateSubscriptionComponent


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amended_by_order_on** | **str** | The date when the rate plan charge is amended through an order or amendment. This field is to standardize the booking date information to increase audit ability and traceability of data between Zuora Billing and Zuora Revenue. It is mapped as the booking date for a sale order line in Zuora Revenue.  | [optional] 
**apply_discount_to** | **str** | Specifies the type of charges that you want a specific discount to apply to.  Values:  * &#x60;ONETIME&#x60; * &#x60;RECURRING&#x60; * &#x60;USAGE&#x60; * &#x60;ONETIMERECURRING&#x60; * &#x60;ONETIMEUSAGE&#x60; * &#x60;RECURRINGUSAGE&#x60; * &#x60;ONETIMERECURRINGUSAGE&#x60;  | [optional] 
**bill_cycle_day** | **str** | Sets the bill cycle day (BCD) for the charge. The BCD determines which day of the month the customer is billed.  Values: &#x60;1&#x60;-&#x60;31&#x60;  | [optional] 
**bill_cycle_type** | **str** | Specifies how to determine the billing day for the charge. When this field is set to &#x60;SpecificDayofMonth&#x60;, set the &#x60;BillCycleDay&#x60; field. When this field is set to &#x60;SpecificDayofWeek&#x60;, set the &#x60;weeklyBillCycleDay&#x60; field.  Values:  * &#x60;DefaultFromCustomer&#x60; * &#x60;SpecificDayofMonth&#x60; * &#x60;SubscriptionStartDay&#x60; * &#x60;ChargeTriggerDay&#x60; * &#x60;SpecificDayofWeek&#x60;  | [optional] 
**billing_period** | **str** | Billing period for the charge. The start day of the billing period is also called the bill cycle day (BCD). Values:  * &#x60;Month&#x60; * &#x60;Quarter&#x60; * &#x60;Semi_Annual&#x60; * &#x60;Annual&#x60; * &#x60;Eighteen_Months&#x60; * &#x60;Two_Years&#x60; * &#x60;Three_Years&#x60; * &#x60;Five_Years&#x60; * &#x60;Specific_Months&#x60; * &#x60;Subscription_Term&#x60; * &#x60;Week&#x60; * &#x60;Specific_Weeks&#x60;  | [optional] 
**billing_period_alignment** | **str** | Aligns charges within the same subscription if multiple charges begin on different dates.  Values:  * &#x60;AlignToCharge&#x60; * &#x60;AlignToSubscriptionStart&#x60; * &#x60;AlignToTermStart&#x60;  | [optional] 
**billing_timing** | **str** | Billing timing for the charge for recurring charge types. Not avaliable for one time, usage, and discount charges.  Values:  * &#x60;IN_ADVANCE&#x60; (default) * &#x60;IN_ARREARS&#x60;  | [optional] 
**charge_model_configuration** | [**ChargeModelConfigurationForSubscription**](ChargeModelConfigurationForSubscription.md) |  | [optional] 
**description** | **str** | Description of the charge.  | [optional] 
**discount_amount** | **float** | Specifies the amount of fixed-amount discount.  | [optional] 
**discount_level** | **str** | Specifies if the discount applies to the product rate plan only, the entire subscription, or to any activity in the account.  Values:  * &#x60;rateplan&#x60; * &#x60;subscription&#x60; * &#x60;account&#x60;  | [optional] 
**discount_percentage** | **float** | Percentage of discount for a percentage discount.   | [optional] 
**end_date_condition** | **str** | Defines when the charge ends after the charge trigger date. If the subscription ends before the charge end date, the charge ends when the subscription ends. But if the subscription end date is subsequently changed through a Renewal, or Terms and Conditions amendment, the charge will end on the charge end date.  Values:  * &#x60;Subscription_End&#x60; * &#x60;Fixed_Period&#x60; * &#x60;Specific_End_Date&#x60; * &#x60;One_Time&#x60;  | [optional] 
**exclude_item_billing_from_revenue_accounting** | **bool** | The flag to exclude rate plan charge related invoice items, invoice item adjustments, credit memo items, and debit memo items from revenue accounting.  **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled.  | [optional] 
**exclude_item_booking_from_revenue_accounting** | **bool** | The flag to exclude rate plan charges from revenue accounting.  **Note**: This field is only available if you have the Billing - Revenue Integration feature enabled.  | [optional] 
**included_units** | **float** | Specifies the number of units in the base set of units for this charge. Must be &gt;&#x3D;&#x60;0&#x60;.  | [optional] 
**is_allocation_eligible** | **bool** | This field is used to identify if the charge segment is allocation eligible in revenue recognition.  **Note**: This feature is in the **Early Adopter** phase. If you want to use the feature, submit a request at &lt;a href&#x3D;\&quot;https://support.zuora.com/\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Zuora Global Support&lt;/a&gt;, and we will evaluate whether the feature is suitable for your use cases.  | [optional] 
**is_unbilled** | **bool** | This field is used to dictate how to perform the accounting during revenue recognition.  **Note**: This feature is in the **Early Adopter** phase. If you want to use the feature, submit a request at &lt;a href&#x3D;\&quot;https://support.zuora.com/\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Zuora Global Support&lt;/a&gt;, and we will evaluate whether the feature is suitable for your use cases.  | [optional] 
**list_price_base** | **str** | The list price base for the product rate plan charge.  Values:  * &#x60;Per_Billing_Period&#x60; * &#x60;Per_Month&#x60; * &#x60;Per_Week&#x60; * &#x60;Per_Year&#x60; * &#x60;Per_Specific_Months&#x60;  | [optional] 
**number** | **str** | Unique number that identifies the charge. Max 50 characters. System-generated if not provided.  | [optional] 
**number_of_periods** | **int** | Specifies the number of periods to use when calculating charges in an overage smoothing charge model.  | [optional] 
**original_order_date** | **date** | The date when the rate plan charge is created through an order or amendment. This field is not updatable.  This field is to standardize the booking date information to increase audit ability and traceability of data between Zuora Billing and Zuora Revenue. It is mapped as the booking date for a sale order line in Zuora Revenue.  | [optional] 
**overage_price** | **float** | Price for units over the allowed amount.  | [optional] 
**overage_unused_units_credit_option** | **str** | Determines whether to credit the customer with unused units of usage.  Values:  * &#x60;NoCredit&#x60; * &#x60;CreditBySpecificRate&#x60;  | [optional] 
**price** | **float** | Price for units in the subscription rate plan.  | [optional] 
**price_change_option** | **str** | Applies an automatic price change when a termed subscription is renewed. The Billing Admin setting **Enable Automatic Price Change When Subscriptions are Renewed?** must be set to Yes to use this field. Values:  * &#x60;NoChange&#x60; (default) * &#x60;SpecificPercentageValue&#x60; * &#x60;UseLatestProductCatalogPricing&#x60;  | [optional] 
**price_increase_percentage** | **float** | Specifies the percentage to increase or decrease the price of a termed subscription&#39;s renewal. Required if you set the &#x60;PriceChangeOption&#x60; field to &#x60;SpecificPercentageValue&#x60;.   Value must be a decimal between &#x60;-100&#x60; and &#x60;100&#x60;.  | [optional] 
**product_rate_plan_charge_id** | **str** | ID of a product rate-plan charge for this subscription.  | 
**product_rate_plan_charge_number** | **str** | Number of a product rate-plan charge for this subscription.  | [optional] 
**quantity** | **float** | Number of units. Must be a decimal &gt;&#x3D;&#x60;0&#x60;.   When using &#x60;chargeOverrides&#x60; for creating subscriptions with recurring charge types, the &#x60;quantity&#x60; field must be populated when the charge model is \&quot;Tiered Pricing\&quot; or \&quot;Volume Pricing\&quot;. It is not required for \&quot;Flat Fee Pricing\&quot; charge model.  | [optional] 
**rating_group** | **str** | Specifies a rating group based on which usage records are rated.  Possible values:  - &#x60;ByBillingPeriod&#x60; (default): The rating is based on all the usages in a billing period. - &#x60;ByUsageStartDate&#x60;: The rating is based on all the usages on the same usage start date.  - &#x60;ByUsageRecord&#x60;: The rating is based on each usage record. - &#x60;ByUsageUpload&#x60;: The rating is based on all the  usages in a uploaded usage file (&#x60;.xls&#x60; or &#x60;.csv&#x60;). - &#x60;ByGroupId&#x60;: The rating is based on all the usages in a custom group.  **Note:**  - The &#x60;ByBillingPeriod&#x60; value can be applied for all charge models.  - The &#x60;ByUsageStartDate&#x60;, &#x60;ByUsageRecord&#x60;, and &#x60;ByUsageUpload&#x60; values can only be applied for per unit, volume pricing, and tiered pricing charge models.  - The &#x60;ByGroupId&#x60; value is only available if you have the Active Rating feature enabled. - Use this field only for Usage charges. One-Time Charges and Recurring Charges return &#x60;NULL&#x60;.  | [optional] 
**specific_billing_period** | **int** | Specifies the number of month or week for the charges billing period. Required if you set the value of the &#x60;billingPeriod&#x60; field to &#x60;Specific_Months&#x60; or &#x60;Specific_Weeks&#x60;.  | [optional] 
**specific_end_date** | **date** | Defines when the charge ends after the charge trigger date.  **note:**  * This field is only applicable when the &#x60;endDateCondition&#x60; field is set to &#x60;Specific_End_Date&#x60;.  * If the subscription ends before the specific end date, the charge ends when the subscription ends. But if the subscription end date is subsequently changed through a Renewal, or Terms and Conditions amendment, the charge will end on the specific end date.  | [optional] 
**specific_list_price_base** | **int** | The number of months for the list price base of the charge. This field is required if you set the value of the &#x60;listPriceBase&#x60; field to &#x60;Per_Specific_Months&#x60;.  **Note**:    - This field is available only if you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Billing/Subscriptions/Product_Catalog/I_Annual_List_Price\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Annual List Price&lt;/a&gt; feature enabled.   - The value of this field is &#x60;null&#x60; if you do not set the value of the &#x60;listPriceBase&#x60; field to &#x60;Per_Specific_Months&#x60;.  | [optional] 
**tiers** | [**List[Tier]**](Tier.md) | Container for Volume, Tiered, or Tiered with Overage charge models. Supports the following charge types:  * One-time * Recurring * Usage-based  | [optional] 
**trigger_date** | **date** | Specifies when to start billing the customer for the charge. Required if the &#x60;triggerEvent&#x60; field is set to &#x60;USD&#x60;.  | [optional] 
**trigger_event** | **str** | Specifies when to start billing the customer for the charge.  Values:  * &#x60;UCE&#x60; * &#x60;USA&#x60; * &#x60;UCA&#x60; * &#x60;USD&#x60;  | [optional] 
**unused_units_credit_rates** | **float** | Specifies the rate to credit a customer for unused units of usage. This field applies only for overage charge models when the &#x60;OverageUnusedUnitsCreditOption&#x60; field is set to &#x60;CreditBySpecificRate&#x60;.  | [optional] 
**up_to_periods** | **int** | Specifies the length of the period during which the charge is active. If this period ends before the subscription ends, the charge ends when this period ends.  **Note:** You must use this field together with the &#x60;upToPeriodsType&#x60; field to specify the time period.  * This field is applicable only when the &#x60;endDateCondition&#x60; field is set to &#x60;Fixed_Period&#x60;.  * If the subscription end date is subsequently changed through a Renewal, or Terms and Conditions amendment, the charge end date will change accordingly up to the original period end.  | [optional] 
**up_to_periods_type** | **str** |  The period type used to define when the charge ends.   Values:  * &#x60;Billing_Periods&#x60; * &#x60;Days&#x60; * &#x60;Weeks&#x60; * &#x60;Months&#x60; * &#x60;Years&#x60;  You must use this field together with the &#x60;upToPeriods&#x60; field to specify the time period.  This field is applicable only when the &#x60;endDateCondition&#x60; field is set to &#x60;Fixed_Period&#x60;.   | [optional] 
**weekly_bill_cycle_day** | **str** | Specifies which day of the week is the bill cycle day (BCD) for the charge.   Values:  * &#x60;Sunday&#x60; * &#x60;Monday&#x60; * &#x60;Tuesday&#x60; * &#x60;Wednesday&#x60; * &#x60;Thursday&#x60; * &#x60;Friday&#x60; * &#x60;Saturday&#x60;  | [optional] 

## Example

```python
from zuora_sdk.models.create_subscription_component import CreateSubscriptionComponent

# TODO update the JSON string below
json = "{}"
# create an instance of CreateSubscriptionComponent from a JSON string
create_subscription_component_instance = CreateSubscriptionComponent.from_json(json)
# print the JSON string representation of the object
print(CreateSubscriptionComponent.to_json())

# convert the object into a dict
create_subscription_component_dict = create_subscription_component_instance.to_dict()
# create an instance of CreateSubscriptionComponent from a dict
create_subscription_component_from_dict = CreateSubscriptionComponent.from_dict(create_subscription_component_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


