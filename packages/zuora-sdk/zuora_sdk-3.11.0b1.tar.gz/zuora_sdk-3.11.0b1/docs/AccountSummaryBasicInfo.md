# AccountSummaryBasicInfo

Container for basic information about the account. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**class__ns** | **str** | Value of the Class field for the corresponding customer account in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**customer_type__ns** | [**AccountObjectNSFieldsCustomerTypeNS**](AccountObjectNSFieldsCustomerTypeNS.md) |  | [optional] 
**department__ns** | **str** | Value of the Department field for the corresponding customer account in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**integration_id__ns** | **str** | ID of the corresponding object in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**integration_status__ns** | **str** | Status of the account&#39;s synchronization with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**location__ns** | **str** | Value of the Location field for the corresponding customer account in NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**subsidiary__ns** | **str** | Value of the Subsidiary field for the corresponding customer account in NetSuite. The Subsidiary field is required if you use NetSuite OneWorld. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**sync_date__ns** | **str** | Date when the account was sychronized with NetSuite. Only available if you have installed the [Zuora Connector for NetSuite](https://www.zuora.com/connect/app/?appId&#x3D;265).  | [optional] 
**syncto_net_suite__ns** | [**AccountObjectNSFieldsSynctoNetSuiteNS**](AccountObjectNSFieldsSynctoNetSuiteNS.md) |  | [optional] 
**account_number** | **str** | Account number.  | [optional] 
**additional_email_addresses** | **List[str]** | A list of additional email addresses to receive email notifications.  | [optional] 
**auto_pay** | **bool** | Whether future payments are automatically collected when they are due during a payment run. | [optional] 
**balance** | **decimal.Decimal** | Current outstanding balance.  | [optional] 
**batch** | **str** | The alias name given to a batch. A string of 50 characters or less.  | [optional] 
**bill_cycle_day** | **int** | Billing cycle day (BCD), the day of the month when a bill run generates invoices for the account. | [optional] 
**currency** | **str** | A currency as defined in Billing Settings in the Zuora UI.  | [optional] 
**default_payment_method** | [**AccountSummaryDefaultPaymentMethod**](AccountSummaryDefaultPaymentMethod.md) |  | [optional] 
**id** | **str** | Account ID.  | [optional] 
**invoice_delivery_prefs_email** | **bool** | Whether the customer wants to receive invoices through email.   | [optional] 
**invoice_delivery_prefs_print** | **bool** | Whether the customer wants to receive printed invoices, such as through postal mail. | [optional] 
**last_invoice_date** | **date** | Date of the most recent invoice for the account; null if no invoice has ever been generated. | [optional] 
**last_metrics_update** | **str** | The date and time when account metrics are last updated, if the account is a partner account.   **Note**:    - This field is available only if you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Manage_customer_accounts/AAA_Overview_of_customer_accounts/Reseller_Account\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Reseller Account&lt;/a&gt; feature enabled.   - If you have the Reseller Account feature enabled, and set the &#x60;partnerAccount&#x60; field to &#x60;false&#x60; for an account, the value of the &#x60;lastMetricsUpdate&#x60; field is automatically set to &#x60;null&#x60; in the response.    - If you ever set the &#x60;partnerAccount&#x60; field to &#x60;true&#x60; for an account, the value of &#x60;lastMetricsUpdate&#x60; field is the time when the account metrics are last updated.    | [optional] 
**last_payment_amount** | **decimal.Decimal** | Amount of the most recent payment collected for the account; null if no payment has ever been collected. | [optional] 
**last_payment_date** | **date** | Date of the most recent payment collected for the account. Null if no payment has ever been collected. | [optional] 
**name** | **str** | Account name.  | [optional] 
**partner_account** | **bool** | Whether the customer account is a partner, distributor, or reseller.     **Note**: This field is available only if you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Manage_customer_accounts/AAA_Overview_of_customer_accounts/Reseller_Account\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Reseller Account&lt;/a&gt; feature enabled. | [optional] 
**purchase_order_number** | **str** | The purchase order number provided by your customer for services, products, or both purchased. | [optional] 
**status** | [**AccountStatus**](AccountStatus.md) |  | [optional] 
**tags** | **str** |  | [optional] 
**organization_label** | **str** | organization label.  | [optional] 
**payment_method_cascading_consent** | **bool** | payment method cascading consent  | [optional] 
**customer_service_rep_name** | **str** | customer ServiceRep Name.  | [optional] 

## Example

```python
from zuora_sdk.models.account_summary_basic_info import AccountSummaryBasicInfo

# TODO update the JSON string below
json = "{}"
# create an instance of AccountSummaryBasicInfo from a JSON string
account_summary_basic_info_instance = AccountSummaryBasicInfo.from_json(json)
# print the JSON string representation of the object
print(AccountSummaryBasicInfo.to_json())

# convert the object into a dict
account_summary_basic_info_dict = account_summary_basic_info_instance.to_dict()
# create an instance of AccountSummaryBasicInfo from a dict
account_summary_basic_info_from_dict = AccountSummaryBasicInfo.from_dict(account_summary_basic_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


