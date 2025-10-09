# AccountBasicInfo

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
**batch** | **str** | The alias name given to a batch. A string of 50 characters or less.  | [optional] 
**communication_profile_id** | **str** | The ID of the communication profile that this account is linked to. | [optional] 
**credit_memo_template_id** | **str** | **Note:** This field is only available if you have [Invoice Settlement](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoicbe_Settlement) enabled. The Invoice Settlement feature is generally available as of Zuora Billing Release 296 (March 2021). This feature includes Unapplied Payments, Credit and Debit Memo, and Invoice Item Settlement. If you want to enable Invoice Settlement, see [Invoice Settlement Enablement and Checklist Guide](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement/Invoice_Settlement_Migration_Checklist_and_Guide) for more information.   The unique ID of the credit memo template, configured in **Billing Settings** &gt; **Manage Billing Document Configuration** through the Zuora UI. For example, 2c92c08a6246fdf101626b1b3fe0144b. | [optional] 
**crm_id** | **str** | CRM account ID for the account, up to 100 characters.  | [optional] 
**debit_memo_template_id** | **str** | **Note:** This field is only available if you have [Invoice Settlement](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement) enabled. The Invoice Settlement feature is generally available as of Zuora Billing Release 296 (March 2021). This feature includes Unapplied Payments, Credit and Debit Memo, and Invoice Item Settlement. If you want to enable Invoice Settlement, see [Invoice Settlement Enablement and Checklist Guide](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement/Invoice_Settlement_Migration_Checklist_and_Guide) for more information.   The unique ID of the debit memo template, configured in **Billing Settings** &gt; **Manage Billing Document Configuration** through the Zuora UI. For example, 2c92c08d62470a8501626b19d24f19e2. | [optional] 
**id** | **str** | Account ID.  | [optional] 
**invoice_template_id** | **str** | Invoice template ID, configured in Billing Settings in the Zuora UI.  | [optional] 
**last_metrics_update** | **str** | The date and time when account metrics are last updated, if the account is a partner account.   **Note**:    - This field is available only if you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Manage_customer_accounts/AAA_Overview_of_customer_accounts/Reseller_Account\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Reseller Account&lt;/a&gt; feature enabled.   - If you have the Reseller Account feature enabled, and set the &#x60;partnerAccount&#x60; field to &#x60;false&#x60; for an account, the value of the &#x60;lastMetricsUpdate&#x60; field is automatically set to &#x60;null&#x60; in the response.    - If you ever set the &#x60;partnerAccount&#x60; field to &#x60;true&#x60; for an account, the value of &#x60;lastMetricsUpdate&#x60; field is the time when the account metrics are last updated. | [optional] 
**name** | **str** | Account name.  | [optional] 
**notes** | **str** | Notes associated with the account, up to 65,535 characters.  | [optional] 
**parent_id** | **str** | Identifier of the parent customer account for this Account object. The length is 32 characters. Use this field if you have &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Billing/Subscriptions/Customer_Accounts/A_Customer_Account_Introduction#Customer_Hierarchy\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Customer Hierarchy&lt;/a&gt; enabled. | [optional] 
**partner_account** | **bool** | Whether the customer account is a partner, distributor, or reseller.     **Note**: This field is available only if you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Manage_customer_accounts/AAA_Overview_of_customer_accounts/Reseller_Account\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Reseller Account&lt;/a&gt; feature enabled. | [optional] 
**profile_number** | **str** | The number of the communication profile that this account is linked to. | [optional] 
**purchase_order_number** | **str** | The purchase order number provided by your customer for services, products, or both purchased. | [optional] 
**sales_rep** | **str** | The name of the sales representative associated with this account, if applicable. Maximum of 50 characters. | [optional] 
**sequence_set_id** | **str** | The ID of the billing document sequence set that is assigned to the customer account.  | [optional] 
**status** | [**AccountStatus**](AccountStatus.md) |  | [optional] 
**tags** | **str** |  | [optional] 
**customer_service_rep_name** | **str** | customer ServiceRep Name.  | [optional] 
**organization_label** | **str** | organization label.  | [optional] 
**summary_statement_template_id** | **str** | summary statement template ID.  | [optional] 

## Example

```python
from zuora_sdk.models.account_basic_info import AccountBasicInfo

# TODO update the JSON string below
json = "{}"
# create an instance of AccountBasicInfo from a JSON string
account_basic_info_instance = AccountBasicInfo.from_json(json)
# print the JSON string representation of the object
print(AccountBasicInfo.to_json())

# convert the object into a dict
account_basic_info_dict = account_basic_info_instance.to_dict()
# create an instance of AccountBasicInfo from a dict
account_basic_info_from_dict = AccountBasicInfo.from_dict(account_basic_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


