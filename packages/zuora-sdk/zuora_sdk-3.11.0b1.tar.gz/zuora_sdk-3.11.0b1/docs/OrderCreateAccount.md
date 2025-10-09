# OrderCreateAccount


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_number** | **str** |  | [optional] 
**additional_email_addresses** | **str** | List of additional email addresses to receive emailed invoices. Values should be a comma-separated list of email addresses. | [optional] 
**allow_invoice_edit** | **bool** | Indicates if associated invoices can be edited. Values are:   * &#x60;true&#x60; * &#x60;false&#x60; (default)  | [optional] 
**auto_pay** | **bool** | Specifies whether future payments are to be automatically billed when they are due. Possible values are &#x60;true&#x60;, &#x60;false&#x60;. | [optional] 
**batch** | **str** |  | [optional] 
**bill_cycle_day** | **int** | Day of the month that the account prefers billing periods to begin on. If set to 0, the bill cycle day will be set as \&quot;AutoSet\&quot;. | 
**bill_to_contact** | [**OrderCreateAccountContact**](OrderCreateAccountContact.md) |  | 
**communication_profile_id** | **str** |  | [optional] 
**credit_card** | [**CreditCard**](CreditCard.md) |  | [optional] 
**credit_memo_template_id** | **str** | **Note:** This field is only available if you have [Invoice Settlement](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement) enabled. The Invoice Settlement feature is generally available as of Zuora Billing Release 296 (March 2021). This feature includes Unapplied Payments, Credit and Debit Memo, and Invoice Item Settlement. If you want to enable Invoice Settlement, see [Invoice Settlement Enablement and Checklist Guide](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement/Invoice_Settlement_Migration_Checklist_and_Guide) for more information.   The unique ID of the credit memo template, configured in **Billing Settings** &gt; **Manage Billing Document Configuration** through the Zuora UI. For example, 2c92c08a6246fdf101626b1b3fe0144b. | [optional] 
**crm_id** | **str** |  | [optional] 
**currency** | **str** | 3 uppercase character currency code.   For payment method authorization, if the &#x60;paymentMethod&#x60; &gt; &#x60;currencyCode&#x60; field is specified, &#x60;currencyCode&#x60; is used. Otherwise, this &#x60;currency&#x60; field is used for payment method authorization. If no currency is specified for the account, the default currency of the account is then used. | 
**custom_fields** | **Dict[str, object]** |  | [optional] 
**customer_service_rep_name** | **str** | Name of the account&#39;s customer service representative, if applicable.  | [optional] 
**debit_memo_template_id** | **str** | **Note:** This field is only available if you have [Invoice Settlement](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement) enabled. The Invoice Settlement feature is generally available as of Zuora Billing Release 296 (March 2021). This feature includes Unapplied Payments, Credit and Debit Memo, and Invoice Item Settlement. If you want to enable Invoice Settlement, see [Invoice Settlement Enablement and Checklist Guide](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement/Invoice_Settlement_Migration_Checklist_and_Guide) for more information.   The unique ID of the debit memo template, configured in **Billing Settings** &gt; **Manage Billing Document Configuration** through the Zuora UI. For example, 2c92c08d62470a8501626b19d24f19e2. | [optional] 
**hpm_credit_card_payment_method_id** | **str** | The ID of the payment method associated with this account. The payment method specified for this field will be set as the default payment method of the account.   If the &#x60;autoPay&#x60; field is set to &#x60;true&#x60;, you must provide the credit card payment method ID for either this field or the &#x60;creditCard&#x60; field,  but not both.   For the Credit Card Reference Transaction payment method, you can specify the payment method ID in this field or use the &#x60;paymentMethod&#x60; field to create a CC Reference Transaction payment method for an account. | [optional] 
**invoice_delivery_prefs_email** | **bool** | Specifies whether to turn on the invoice delivery method &#39;Email&#39; for the new account.   Values are:    * &#x60;true&#x60; (default). Turn on the invoice delivery method &#39;Email&#39; for the new account.  * &#x60;false&#x60;. Turn off the invoice delivery method &#39;Email&#39; for the new account. | [optional] 
**invoice_delivery_prefs_print** | **bool** | Specifies whether to turn on the invoice delivery method &#39;Print&#39; for the new account.  Values are:    * &#x60;true&#x60;. Turn on the invoice delivery method &#39;Print&#39; for the new account.  * &#x60;false&#x60; (default). Turn off the invoice delivery method &#39;Print&#39; for the new account. | [optional] 
**invoice_template_id** | **str** |  | [optional] 
**name** | **str** |  | 
**notes** | **str** |  | [optional] 
**parent_id** | **str** | Identifier of the parent customer account for this Account object. Use this field if you have &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Billing/Subscriptions/Customer_Accounts/A_Customer_Account_Introduction#Customer_Hierarchy\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Customer Hierarchy&lt;/a&gt; enabled. | [optional] 
**partner_account** | **bool** | Whether the customer account is a partner, distributor, or reseller.  You can set this field to &#x60;true&#x60; if you have business with distributors or resellers, or operating in B2B model to manage numerous subscriptions through concurrent API requests. After this field is set to &#x60;true&#x60;, the calculation of account metrics is performed asynchronously during operations such as subscription creation, order changes, invoice generation, and payments.  **Note**: This field is available only if you have the &lt;a href&#x3D;\&quot;https://knowledgecenter.zuora.com/Zuora_Billing/Manage_customer_accounts/AAA_Overview_of_customer_accounts/Reseller_Account\&quot; target&#x3D;\&quot;_blank\&quot;&gt;Reseller Account&lt;/a&gt; feature enabled. | [optional] 
**payment_gateway** | **str** |  | [optional] 
**payment_method** | [**CreateAccountPaymentMethod**](CreateAccountPaymentMethod.md) |  | [optional] 
**payment_term** | **str** | **Note**: If you want to specify a payment term when creating a new account, you must set a value in this field. If you do not set a value in this field, Zuora will use &#x60;Due Upon Receipt&#x60; as the value instead of the default value set in **Billing Settings** &gt; **Payment Terms** from Zuora UI. | [optional] 
**purchase_order_number** | **str** | The number of the purchase order associated with this account. Purchase order information generally comes from customers. | [optional] 
**sales_rep** | **str** | The name of the sales representative associated with this account, if applicable. | [optional] 
**sequence_set_id** | **str** | The ID of the sequence set to assign to the customer account.    The billing documents to generate for this account will adopt the prefix and starting document number configured in the sequence set. | [optional] 
**sold_to_contact** | [**OrderCreateAccountContact**](OrderCreateAccountContact.md) |  | [optional] 
**sold_to_same_as_bill_to** | **bool** | Whether the sold-to contact and bill-to contact are the same entity.    The created account has the same bill-to contact and sold-to contact entity only when all the following conditions are met in the request body:   - This field is set to &#x60;true&#x60;.   - A bill-to contact is specified.  - No sold-to contact is specified. | [optional] 
**ship_to_contact** | [**OrderCreateAccountContact**](OrderCreateAccountContact.md) |  | [optional] 
**ship_to_same_as_bill_to** | **bool** | The created account has the same ship-to contact and bill-to contact | [optional] 
**tax_info** | [**TaxInfo**](TaxInfo.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.order_create_account import OrderCreateAccount

# TODO update the JSON string below
json = "{}"
# create an instance of OrderCreateAccount from a JSON string
order_create_account_instance = OrderCreateAccount.from_json(json)
# print the JSON string representation of the object
print(OrderCreateAccount.to_json())

# convert the object into a dict
order_create_account_dict = order_create_account_instance.to_dict()
# create an instance of OrderCreateAccount from a dict
order_create_account_from_dict = OrderCreateAccount.from_dict(order_create_account_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


