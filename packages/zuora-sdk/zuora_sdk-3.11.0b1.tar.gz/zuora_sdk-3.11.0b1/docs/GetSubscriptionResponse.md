# GetSubscriptionResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**cpq_bundle_json_id__qt** | **str** | The Bundle product structures from Zuora Quotes if you utilize Bundling in Salesforce. Do not change the value in this field. | [optional] 
**opportunity_close_date__qt** | **date** | The closing date of the Opportunity. This field is used in Zuora data sources to report on Subscription metrics. If the subscription originated from Zuora Quotes, the value is populated with the value from Zuora Quotes. | [optional] 
**opportunity_name__qt** | **str** | The unique identifier of the Opportunity. This field is used in Zuora data sources to report on Subscription metrics. If the subscription originated from Zuora Quotes, the value is populated with the value from Zuora Quotes. | [optional] 
**quote_business_type__qt** | **str** | The specific identifier for the type of business transaction the Quote represents such as New, Upsell, Downsell, Renewal or Churn. This field is used in Zuora data sources to report on Subscription metrics. If the subscription originated from Zuora Quotes, the value is populated with the value from Zuora Quotes. | [optional] 
**quote_number__qt** | **str** | The unique identifier of the Quote. This field is used in Zuora data sources to report on Subscription metrics. If the subscription originated from Zuora Quotes, the value is populated with the value from Zuora Quotes. | [optional] 
**quote_type__qt** | **str** | The Quote type that represents the subscription lifecycle stage such as New, Amendment, Renew or Cancel. This field is used in Zuora data sources to report on Subscription metrics. If the subscription originated from Zuora Quotes, the value is populated with the value from Zuora Quotes. | [optional] 
**integration_id__ns** | **str** | ID of the corresponding object in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**integration_status__ns** | **str** | Status of the subscription&#39;s synchronization with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**project__ns** | **str** | The NetSuite project that the subscription was created from. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**sales_order__ns** | **str** | The NetSuite sales order than the subscription was created from. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**sync_date__ns** | **str** | Date when the subscription was synchronized with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265). | [optional] 
**id** | **str** | Subscription ID.  | [optional] 
**subscription_number** | **str** | Subscription number. | [optional] 
**account_id** | **str** | The ID of the account associated with this subscription. | [optional] 
**account_name** | **str** | The name of the account associated with this subscription. | [optional] 
**account_number** | **str** | The number of the account associated with this subscription. | [optional] 
**auto_renew** | **bool** | If &#x60;true&#x60;, the subscription automatically renews at the end of the term. Default is &#x60;false&#x60;. | [optional] 
**bill_to_contact** | [**Contact**](Contact.md) |  | [optional] 
**cancel_reason** | **str** | The reason for a subscription cancellation copied from the &#x60;changeReason&#x60; field of a Cancel Subscription order action.    This field contains valid value only if a subscription is cancelled through the Orders UI or API. Otherwise, the value for this field will always be &#x60;null&#x60;. | [optional] 
**communication_profile_id** | **str** | The ID of the communication profile associated with the subscription.  **Note**: This field is available only if you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Bill_your_customers/Bill_customers_at_subscription_level/Flexible_Billing_Attributes\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Flexible Billing Attributes&lt;/a&gt; feature enabled.  | [optional] 
**contract_effective_date** | **date** | Effective contract date for this subscription, as yyyy-mm-dd.  | [optional] 
**contracted_mrr** | **float** | Monthly recurring revenue of the subscription.  | [optional] 
**current_term** | **int** | The length of the period for the current subscription term.  | [optional] 
**current_term_period_type** | [**TermPeriodType**](TermPeriodType.md) |  | [optional] 
**customer_acceptance_date** | **date** | The date on which the services or products within a subscription have been accepted by the customer, as yyyy-mm-dd. | [optional] 
**currency** | **str** | The currency of the subscription.  | [optional] 
**create_time** | **str** | The date when the subscription was created, as yyyy-mm-dd HH:MM:SS.  | [optional] 
**update_time** | **str** | The date when the subscription was last updated, as yyyy-mm-dd HH:MM:SS.  | [optional] 
**externally_managed_by** | [**ExternallyManagedBy**](ExternallyManagedBy.md) |  | [optional] 
**initial_term** | **int** | The length of the period for the first subscription term.  | [optional] 
**initial_term_period_type** | [**TermPeriodType**](TermPeriodType.md) |  | [optional] 
**invoice_group_number** | **str** | The number of invoice group associated with the subscription.  **Note**: This field is available only if you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Bill_your_customers/Bill_customers_at_subscription_level/Flexible_Billing_Attributes\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Flexible Billing Attributes&lt;/a&gt; feature enabled.  | [optional] 
**invoice_owner_account_id** | **str** |  | [optional] 
**invoice_owner_account_name** | **str** |  | [optional] 
**invoice_owner_account_number** | **str** |  | [optional] 
**invoice_schedule_id** | **str** | The ID of the invoice schedule associated with the subscription.   If multiple invoice schedules are created for different terms of a subscription, this field stores the latest invoice schedule.   **Note**: This field is available only if you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Billing_Schedule\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Billing Schedule&lt;/a&gt; feature in the **Early Adopter** phase enabled. | [optional] 
**invoice_separately** | **str** | Separates a single subscription from other subscriptions and creates an invoice for the subscription.    If the value is &#x60;true&#x60;, the subscription is billed separately from other subscriptions. If the value is &#x60;false&#x60;, the subscription is included with other subscriptions in the account invoice. | [optional] 
**invoice_template_id** | **str** | The ID of the invoice template associated with the subscription.  **Note**:    - If you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Bill_your_customers/Bill_customers_at_subscription_level/Flexible_Billing_Attributes\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Flexible Billing Attributes&lt;/a&gt; feature disabled, this field is unavailable in the request body and the value of this field is &#x60;null&#x60; in the response body.    - If you have the Flexible Billing Attributes feature enabled, and you do not specify this field in the request or you select **Default Template from Account** for this field during subscription creation, the value of this field is automatically set to &#x60;null&#x60; in the response body.  | [optional] 
**invoice_template_name** | **str** | The name of the invoice template associated with the subscription.  **Note**:    - If you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Bill_your_customers/Bill_customers_at_subscription_level/Flexible_Billing_Attributes\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Flexible Billing Attributes&lt;/a&gt; feature disabled, the value of this field is &#x60;null&#x60; in the response body.    - If you have the Flexible Billing Attributes feature enabled, and you do not specify the &#x60;invoiceTemplateId&#x60; field in the request or you select **Default Template from Account** for the &#x60;invoiceTemplateId&#x60; field during subscription creation, the value of the &#x60;invoiceTemplateName&#x60; field is automatically set to &#x60;null&#x60; in the response body.     | [optional] 
**is_latest_version** | **bool** | If &#x60;true&#x60;, the current subscription object is the latest version. | [optional] 
**last_booking_date** | **date** | The last booking date of the subscription object. This field is writable only when the subscription is newly created as a first version subscription. You can override the date value when creating a subscription through the Subscribe and Amend API or the subscription creation UI (non-Orders). Otherwise, the default value &#x60;today&#x60; is set per the user&#39;s timezone. The value of this field is as follows:  * For a new subscription created by the [Subscribe and Amend APIs](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/Orders_Harmonization/Orders_Migration_Guidance#Subscribe_and_Amend_APIs_to_Migrate), this field has the value of the subscription creation date.  * For a subscription changed by an amendment, this field has the value of the amendment booking date.  * For a subscription created or changed by an order, this field has the value of the order date.  | [optional] 
**notes** | **str** | A string of up to 65,535 characters.  | [optional] 
**order_number** | **str** | The order number of the order in which the changes on the subscription are made.    **Note:** This field is only available if you have the [Order Metrics](https://knowledgecenter.zuora.com/BC_Subscription_Management/Orders/AA_Overview_of_Orders#Order_Metrics) feature enabled. If you wish to have access to the feature, submit a request at [Zuora Global Support](http://support.zuora.com/). We will investigate your use cases and data before enabling this feature for you. | [optional] 
**payment_term** | **str** | The name of the payment term associated with the subscription. For example, &#x60;Net 30&#x60;. The payment term determines the due dates of invoices.   **Note**:    - If you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Bill_your_customers/Bill_customers_at_subscription_level/Flexible_Billing_Attributes\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Flexible Billing Attributes&lt;/a&gt; feature disabled, this field is unavailable in the request body and the value of this field is &#x60;null&#x60; in the response body.    - If you have the Flexible Billing Attributes feature enabled, and you do not specify this field in the request or you select **Default Term from Account** for this field during subscription creation, the value of this field is automatically set to &#x60;null&#x60; in the response body. | [optional] 
**rate_plans** | [**List[SubscriptionRatePlan]**](SubscriptionRatePlan.md) | Container for rate plans.  | [optional] 
**renewal_setting** | **str** | Specifies whether a termed subscription will remain &#x60;TERMED&#x60; or change to &#x60;EVERGREEN&#x60; when it is renewed.    Values are:   * &#x60;RENEW_WITH_SPECIFIC_TERM&#x60; (default)  * &#x60;RENEW_TO_EVERGREEN&#x60; | [optional] 
**renewal_term** | **int** | The length of the period for the subscription renewal term.  | [optional] 
**renewal_term_period_type** | [**TermPeriodType**](TermPeriodType.md) |  | [optional] 
**revision** | **str** | An auto-generated decimal value uniquely tagged with a subscription. The value always contains one decimal place, for example, the revision of a new subscription is 1.0. If a further version of the subscription is created, the revision value will be increased by 1. Also, the revision value is always incremental regardless of deletion of subscription versions. | [optional] 
**sequence_set_id** | **str** | The ID of the sequence set associated with the subscription.  **Note**:    - If you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Bill_your_customers/Bill_customers_at_subscription_level/Flexible_Billing_Attributes\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Flexible Billing Attributes&lt;/a&gt; feature disabled, this field is unavailable in the request body and the value of this field is &#x60;null&#x60; in the response body.    - If you have the Flexible Billing Attributes feature enabled, and you do not specify this field in the request or you select **Default Set from Account** for this field during subscription creation, the value of this field is automatically set to &#x60;null&#x60; in the response body.  | [optional] 
**sequence_set_name** | **str** | The name of the sequence set associated with the subscription.  **Note**:    - If you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Bill_your_customers/Bill_customers_at_subscription_level/Flexible_Billing_Attributes\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Flexible Billing Attributes&lt;/a&gt; feature disabled, the value of this field is &#x60;null&#x60; in the response body.    - If you have the Flexible Billing Attributes feature enabled, and you do not specify the &#x60;sequenceSetId&#x60; field in the request or you select **Default Template from Account** for the &#x60;sequenceSetId&#x60; field during subscription creation, the value of the &#x60;sequenceSetName&#x60; field is automatically set to &#x60;null&#x60; in the response body.  | [optional] 
**service_activation_date** | **date** | The date on which the services or products within a subscription have been activated and access has been provided to the customer, as yyyy-mm-dd | [optional] 
**sold_to_contact** | [**Contact**](Contact.md) |  | [optional] 
**ship_to_contact** | [**Contact**](Contact.md) |  | [optional] 
**status** | [**SubscriptionStatus**](SubscriptionStatus.md) |  | [optional] 
**status_history** | [**List[SubscriptionStatusHistory]**](SubscriptionStatusHistory.md) | Container for status history.  | [optional] 
**subscription_start_date** | **date** | Date the subscription becomes effective.  | [optional] 
**subscription_end_date** | **date** | The date when the subscription term ends, where the subscription ends at midnight the day before.  For example, if the &#x60;subscriptionEndDate&#x60; is 12/31/2016, the subscriptions ends at midnight (00:00:00 hours) on 12/30/2016.  This date is the same as the term end date or the cancelation date, as appropriate. | [optional] 
**term_end_date** | **date** | Date the subscription term ends. If the subscription is evergreen, this is null or is the cancellation date (if one has been set). | [optional] 
**term_start_date** | **date** | Date the subscription term begins. If this is a renewal subscription, this date is different from the subscription start date. | [optional] 
**term_type** | **str** | Possible values are: &#x60;TERMED&#x60;, &#x60;EVERGREEN&#x60;.  | [optional] 
**scheduled_cancel_date** | **date** |  | [optional] 
**scheduled_suspend_date** | **date** |  | [optional] 
**scheduled_resume_date** | **date** |  | [optional] 
**total_contracted_value** | **float** | Total contracted value of the subscription.  | [optional] 
**version** | **int** | This is the subscription version automatically generated by Zuora Billing. Each order or amendment creates a new version of the subscription, which incorporates the changes made in the order or amendment. | [optional] 
**contracted_net_mrr** | **float** | Monthly recurring revenue of the subscription inclusive of all the discounts applicable, including the fixed-amount discounts and percentage discounts.  | [optional] 
**as_of_day_gross_mrr** | **float** | Monthly recurring revenue of the subscription exclusive of any discounts applicable as of specified day.  | [optional] 
**as_of_day_net_mrr** | **float** | Monthly recurring revenue of the subscription inclusive of all the discounts applicable, including the fixed-amount discounts and percentage discounts as of specified day.  | [optional] 
**net_total_contracted_value** | **float** | Total contracted value of the subscription inclusive of all the discounts applicable, including the fixed-amount discounts and percentage discounts.  | [optional] 
**account_owner_details** | [**AccountBasicInfo**](AccountBasicInfo.md) |  | [optional] 
**invoice_owner_account_details** | [**AccountBasicInfo**](AccountBasicInfo.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.get_subscription_response import GetSubscriptionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetSubscriptionResponse from a JSON string
get_subscription_response_instance = GetSubscriptionResponse.from_json(json)
# print the JSON string representation of the object
print(GetSubscriptionResponse.to_json())

# convert the object into a dict
get_subscription_response_dict = get_subscription_response_instance.to_dict()
# create an instance of GetSubscriptionResponse from a dict
get_subscription_response_from_dict = GetSubscriptionResponse.from_dict(get_subscription_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


