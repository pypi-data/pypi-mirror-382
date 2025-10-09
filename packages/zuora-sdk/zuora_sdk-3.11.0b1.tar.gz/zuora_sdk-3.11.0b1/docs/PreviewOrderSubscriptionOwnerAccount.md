# PreviewOrderSubscriptionOwnerAccount

Information about a new account that will own the subscription. Only available if you have enabled the Owner Transfer feature.   **Note:** The Owner Transfer feature is in **Limited Availability**. If you wish to have access to the feature, submit a request at [Zuora Global Support](http://support.zuora.com/).   If you do not set this field or the `subscriptionOwnerAccountNumber` field, the account that owns the order will also own the subscription. Zuora will return an error if you set this field and the `subscriptionOwnerAccountNumber` field.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_number** | **str** | Account number. For example, A00000001.  | [optional] 
**additional_email_addresses** | **str** | List of additional email addresses to receive emailed invoices. Values should be a comma-separated list of email addresses. | [optional] 
**allow_invoice_edit** | **bool** | Indicates if associated invoices can be edited. Values are:   * &#x60;true&#x60; * &#x60;false&#x60; (default)  | [optional] 
**auto_pay** | **bool** | Specifies whether future payments are automatically billed when they are due. | [optional] 
**batch** | **str** | Name of the billing batch that the account belongs to. For example, Batch1. | [optional] 
**bill_cycle_day** | **int** | Day of the month that the account prefers billing periods to begin on. If set to 0, the bill cycle day will be set as \&quot;AutoSet\&quot;. | 
**bill_to_contact** | [**OrderCreateAccountContact**](OrderCreateAccountContact.md) |  | 
**communication_profile_id** | **str** | Internal identifier of the communication profile that Zuora uses when sending notifications to the account&#39;s contacts. | [optional] 
**credit_card** | [**CreditCard**](CreditCard.md) |  | [optional] 
**credit_memo_template_id** | **str** | **Note:** This field is only available if you have [Invoice Settlement](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement) enabled. The Invoice Settlement feature is generally available as of Zuora Billing Release 296 (March 2021). This feature includes Unapplied Payments, Credit and Debit Memo, and Invoice Item Settlement. If you want to enable Invoice Settlement, see [Invoice Settlement Enablement and Checklist Guide](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement/Invoice_Settlement_Migration_Checklist_and_Guide) for more information.   The unique ID of the credit memo template, configured in **Billing Settings** &gt; **Manage Billing Document Configuration** through the Zuora UI. For example, 2c92c08a6246fdf101626b1b3fe0144b. | [optional] 
**crm_id** | **str** | External identifier of the account in a CRM system.  | [optional] 
**currency** | **str** | ISO 3-letter currency code (uppercase). For example, USD.  | 
**custom_fields** | **Dict[str, object]** | Container for custom fields of an Account object.  | [optional] 
**customer_service_rep_name** | **str** | Name of the account&#39;s customer service representative, if applicable.  | [optional] 
**debit_memo_template_id** | **str** | **Note:** This field is only available if you have [Invoice Settlement](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement) enabled. The Invoice Settlement feature is generally available as of Zuora Billing Release 296 (March 2021). This feature includes Unapplied Payments, Credit and Debit Memo, and Invoice Item Settlement. If you want to enable Invoice Settlement, see [Invoice Settlement Enablement and Checklist Guide](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement/Invoice_Settlement_Migration_Checklist_and_Guide) for more information.   The unique ID of the debit memo template, configured in **Billing Settings** &gt; **Manage Billing Document Configuration** through the Zuora UI. For example, 2c92c08d62470a8501626b19d24f19e2. | [optional] 
**hpm_credit_card_payment_method_id** | **str** | The ID of the payment method associated with this account. The payment method specified for this field will be set as the default payment method of the account.   If the &#x60;autoPay&#x60; field is set to &#x60;true&#x60;, you must provide the credit card payment method ID for either this field or the &#x60;creditCard&#x60; field,  but not both.   For a specified credit card payment method, it is recommended that [the support for stored credential transactions](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/L_Payment_Methods/Stored_credential_transactions) for this payment method is already enabled. | [optional] 
**invoice_delivery_prefs_email** | **bool** | Specifies whether to turn on the invoice delivery method &#39;Email&#39; for the new account.   Values are:    * &#x60;true&#x60; (default). Turn on the invoice delivery method &#39;Email&#39; for the new account.  * &#x60;false&#x60;. Turn off the invoice delivery method &#39;Email&#39; for the new account.          | [optional] 
**invoice_delivery_prefs_print** | **bool** | Specifies whether to turn on the invoice delivery method &#39;Print&#39; for the new account.  Values are:    * &#x60;true&#x60;. Turn on the invoice delivery method &#39;Print&#39; for the new account.  * &#x60;false&#x60; (default). Turn off the invoice delivery method &#39;Print&#39; for the new account. | [optional] 
**invoice_template_id** | **str** | Internal identifier of the invoice template that Zuora uses when generating invoices for the account. | [optional] 
**name** | **str** | Account name.  | 
**notes** | **str** | Notes about the account. These notes are only visible to Zuora users.  | [optional] 
**parent_id** | **str** | Identifier of the parent customer account for this Account object. Use this field if you have &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Billing/Subscriptions/Customer_Accounts/A_Customer_Account_Introduction#Customer_Hierarchy\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Customer Hierarchy&lt;/a&gt; enabled. | [optional] 
**payment_gateway** | **str** | The payment gateway that Zuora uses when processing electronic payments and refunds for the account. If you do not specify this field or if the value of this field is null, Zuora uses your default payment gateway. | [optional] 
**payment_method** | [**CreateAccountPaymentMethod**](CreateAccountPaymentMethod.md) |  | [optional] 
**payment_term** | **str** | Name of the payment term associated with the account. For example, \&quot;Net 30\&quot;. The payment term determines the due dates of invoices. | [optional] 
**purchase_order_number** | **str** | The number of the purchase order associated with this account. Purchase order information generally comes from customers. | [optional] 
**sales_rep** | **str** | The name of the sales representative associated with this account, if applicable. | [optional] 
**sold_to_contact** | [**OrderCreateAccountContact**](OrderCreateAccountContact.md) |  | [optional] 
**tax_info** | [**TaxInfo**](TaxInfo.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.preview_order_subscription_owner_account import PreviewOrderSubscriptionOwnerAccount

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewOrderSubscriptionOwnerAccount from a JSON string
preview_order_subscription_owner_account_instance = PreviewOrderSubscriptionOwnerAccount.from_json(json)
# print the JSON string representation of the object
print(PreviewOrderSubscriptionOwnerAccount.to_json())

# convert the object into a dict
preview_order_subscription_owner_account_dict = preview_order_subscription_owner_account_instance.to_dict()
# create an instance of PreviewOrderSubscriptionOwnerAccount from a dict
preview_order_subscription_owner_account_from_dict = PreviewOrderSubscriptionOwnerAccount.from_dict(preview_order_subscription_owner_account_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


