# AccountData

The information of the account that you are to create through the \"Sign up\" operation.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_number** | **str** |  | [optional] 
**auto_pay** | **bool** | Specifies whether future payments are to be automatically billed when they are due. Possible values are &#x60;true&#x60;, &#x60;false&#x60;. | [optional] 
**batch** | **str** |  | [optional] 
**bill_cycle_day** | **int** | Day of the month that the account prefers billing periods to begin on. If set to 0, the bill cycle day will be set as \&quot;AutoSet\&quot;. | 
**bill_to_contact** | [**ContactInfo**](ContactInfo.md) |  | 
**communication_profile_id** | **str** |  | [optional] 
**credit_memo_template_id** | **str** | **Note:** This field is only available if you have [Invoice Settlement](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement) enabled. The Invoice Settlement feature is generally available as of Zuora Billing Release 296 (March 2021). This feature includes Unapplied Payments, Credit and Debit Memo, and Invoice Item Settlement. If you want to enable Invoice Settlement, see [Invoice Settlement Enablement and Checklist Guide](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement/Invoice_Settlement_Migration_Checklist_and_Guide) for more information.   The unique ID of the credit memo template, configured in **Billing Settings** &gt; **Manage Billing Document Configuration** through the Zuora UI. For example, 2c92c08a6246fdf101626b1b3fe0144b. | [optional] 
**crm_id** | **str** |  | [optional] 
**currency** | **str** | 3 uppercase character currency code.   For payment method authorization, if the &#x60;paymentMethod&#x60; &gt; &#x60;currencyCode&#x60; field is specified, &#x60;currencyCode&#x60; is used. Otherwise, this &#x60;currency&#x60; field is used for payment method authorization. If no currency is specified for the account, the default currency of the account is then used. | 
**custom_fields** | **Dict[str, object]** | Container for custom fields.  | [optional] 
**debit_memo_template_id** | **str** | **Note:** This field is only available if you have [Invoice Settlement](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement) enabled. The Invoice Settlement feature is generally available as of Zuora Billing Release 296 (March 2021). This feature includes Unapplied Payments, Credit and Debit Memo, and Invoice Item Settlement. If you want to enable Invoice Settlement, see [Invoice Settlement Enablement and Checklist Guide](https://knowledgecenter.zuora.com/Billing/Billing_and_Payments/Invoice_Settlement/Invoice_Settlement_Migration_Checklist_and_Guide) for more information.   The unique ID of the debit memo template, configured in **Billing Settings** &gt; **Manage Billing Document Configuration** through the Zuora UI. For example, 2c92c08d62470a8501626b19d24f19e2. | [optional] 
**invoice_template_id** | **str** |  | [optional] 
**name** | **str** |  | 
**notes** | **str** |  | [optional] 
**payment_method** | [**SignUpPaymentMethod**](SignUpPaymentMethod.md) |  | [optional] 
**payment_term** | **str** |  | [optional] 
**purchase_order_number** | **str** | The number of the purchase order associated with this account. Purchase order information generally comes from customers. | [optional] 
**sequence_set_id** | **str** | The ID of the billing document sequence set to assign to the customer account.    The billing documents to generate for this account will adopt the prefix and starting document number configured in the sequence set. | [optional] 
**sold_to_contact** | [**ContactInfo**](ContactInfo.md) |  | [optional] 
**ship_to_contact** | [**ContactInfo**](ContactInfo.md) |  | [optional] 
**tax_info** | [**SignUpTaxInfo**](SignUpTaxInfo.md) |  | [optional] 
**organization_label** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.account_data import AccountData

# TODO update the JSON string below
json = "{}"
# create an instance of AccountData from a JSON string
account_data_instance = AccountData.from_json(json)
# print the JSON string representation of the object
print(AccountData.to_json())

# convert the object into a dict
account_data_dict = account_data_instance.to_dict()
# create an instance of AccountData from a dict
account_data_from_dict = AccountData.from_dict(account_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


