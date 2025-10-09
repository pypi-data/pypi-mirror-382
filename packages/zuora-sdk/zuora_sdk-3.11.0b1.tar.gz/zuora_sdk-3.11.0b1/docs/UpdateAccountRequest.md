# UpdateAccountRequest


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
**additional_email_addresses** | **List[str]** | A list of additional email addresses to receive email notifications. Use commas to separate email addresses. | [optional] 
**auto_pay** | **bool** | Whether future payments are to be automatically billed when they are due.  | [optional] 
**batch** | **str** | The alias name given to a batch. A string of 50 characters or less.  | [optional] 
**bill_cycle_day** | **int** | Sets the bill cycle day (BCD) for the charge. The BCD determines  which day of the month the customer is billed. Values: Any activated system-defined bill cycle day （&#x60;1&#x60;-&#x60;31&#x60;） | [optional] 
**bill_to_contact_id** | **str** | The ID of the contact that receives the bill. The contact must be   associated with the account. | [optional] 
**bill_to_contact** | [**UpdateAccountContact**](UpdateAccountContact.md) |  | [optional] 
**ship_to_contact_id** | **str** | The ID of the contact that receives the goods or services. The   contact must be associated with the account. | [optional] 
**ship_to_contact** | [**UpdateAccountContact**](UpdateAccountContact.md) |  | [optional] 
**communication_profile_id** | **str** | The ID of the communication profile that this account is linked to.   You can provide either or both of the &#x60;communicationProfileId&#x60; and &#x60;profileNumber&#x60; fields.   If both are provided, the request will fail if they do not refer to the same communication profile. | [optional] 
**credit_memo_template_id** | **str** | **Note:** This field is only available if you have [Invoice Settlement](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement) enabled. The Invoice Settlement feature is generally available as of Zuora Billing Release 296 (March 2021). This feature includes Unapplied Payments, Credit and Debit Memo, and Invoice Item Settlement. If you want to enable Invoice Settlement, see [Invoice Settlement Enablement and Checklist Guide](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement/Invoice_Settlement_Migration_Checklist_and_Guide) for more information.   The unique ID of the credit memo template, configured in **Billing Settings** &gt; **Manage Billing Document Configuration** through the Zuora UI. For example, 2c92c08a6246fdf101626b1b3fe0144b. | [optional] 
**crm_id** | **str** | CRM account ID for the account, up to 100 characters.  | [optional] 
**customer_service_rep_name** | **str** | Name of the account’s customer service representative, if applicable.  | [optional] 
**debit_memo_template_id** | **str** | **Note:** This field is only available if you have [Invoice Settlement](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement) enabled. The Invoice Settlement feature is generally available as of Zuora Billing Release 296 (March 2021). This feature includes Unapplied Payments, Credit and Debit Memo, and Invoice Item Settlement. If you want to enable Invoice Settlement, see [Invoice Settlement Enablement and Checklist Guide](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement/Invoice_Settlement_Migration_Checklist_and_Guide) for more information.   The unique ID of the debit memo template, configured in **Billing Settings** &gt; **Manage Billing Document Configuration** through the Zuora UI. For example, 2c92c08d62470a8501626b19d24f19e2. | [optional] 
**default_payment_method_id** | **str** | ID of the default payment method for the account.  Values: a valid ID for an existing payment method.  | [optional] 
**invoice_delivery_prefs_email** | **bool** | Whether the customer wants to receive invoices through email.   The default value is &#x60;false&#x60;.  | [optional] 
**invoice_delivery_prefs_print** | **bool** | Whether the customer wants to receive printed invoices, such as through postal mail.   The default value is &#x60;false&#x60;. | [optional] 
**invoice_template_id** | **str** | Invoice template ID, configured in Billing Settings in the Zuora UI.  | [optional] 
**name** | **str** | Account name, up to 255 characters.  | [optional] 
**notes** | **str** | A string of up to 65,535 characters.  | [optional] 
**parent_id** | **str** | Identifier of the parent customer account for this Account object. The length is 32 characters. Use this field if you have &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Billing/Subscriptions/Customer_Accounts/A_Customer_Account_Introduction#Customer_Hierarchy\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Customer Hierarchy&lt;/a&gt; enabled. | [optional] 
**partner_account** | **bool** | Whether the customer account is a partner, distributor, or reseller.   You can set this field to &#x60;true&#x60; if you have business with distributors or resellers, or operating in B2B model to manage numerous subscriptions through concurrent API requests. After this field is set to &#x60;true&#x60;, the calculation of account metrics is performed asynchronously during operations such as subscription creation, order changes, invoice generation, and payments.  **Note**: This field is available only if you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Manage_customer_accounts/AAA_Overview_of_customer_accounts/Reseller_Account\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Reseller Account&lt;/a&gt; feature enabled. | [optional] 
**payment_gateway** | **str** | The name of the payment gateway instance. If null or left unassigned, the Account will use the Default Gateway. | [optional] 
**payment_term** | **str** | Payment terms for this account. Possible values are &#x60;Due Upon Receipt&#x60;, &#x60;Net 30&#x60;, &#x60;Net 60&#x60;, &#x60;Net 90&#x60;. | [optional] 
**profile_number** | **str** | The number of the communication profile that this account is linked to.   You can provide either or both of the &#x60;communicationProfileId&#x60; and &#x60;profileNumber&#x60; fields.   If both are provided, the request will fail if they do not refer to the same communication profile. | [optional] 
**purchase_order_number** | **str** | The purchase order number provided by your customer for services, products, or both purchased. | [optional] 
**roll_up_usage** | **bool** | Whether the usage of the account roll up to its parent account | [optional] 
**sales_rep** | **str** | The name of the sales representative associated with this account, if applicable. Maximum of 50 characters. | [optional] 
**sequence_set_id** | **str** | The ID of the billing document sequence set to assign to the customer account.    The billing documents to generate for this account will adopt the prefix and starting document number configured in the sequence set.   If a customer account has no assigned billing document sequence set, billing documents generated for this account adopt the prefix and starting document number from the default sequence set. | [optional] 
**sold_to_contact_id** | **str** | The ID of the contact that receives the goods or services. The contact   must be associated with the account. | [optional] 
**sold_to_contact** | [**UpdateAccountContact**](UpdateAccountContact.md) |  | [optional] 
**tagging** | **str** |  | [optional] 
**tax_info** | [**TaxInfo**](TaxInfo.md) |  | [optional] 
**payment_gateway_number** | **str** | paymentGatewayNumber  | [optional] 
**summary_statement_template_id** | **str** | summaryStatementTemplateId  | [optional] 
**einvoice_profile** | [**AccountEInvoiceProfile**](AccountEInvoiceProfile.md) |  | [optional] 
**gateway_routing_eligible** | **bool** | Whether gateway routing is eligible for the account  | [optional] 

## Example

```python
from zuora_sdk.models.update_account_request import UpdateAccountRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateAccountRequest from a JSON string
update_account_request_instance = UpdateAccountRequest.from_json(json)
# print the JSON string representation of the object
print(UpdateAccountRequest.to_json())

# convert the object into a dict
update_account_request_dict = update_account_request_instance.to_dict()
# create an instance of UpdateAccountRequest from a dict
update_account_request_from_dict = UpdateAccountRequest.from_dict(update_account_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


