# ExpandedAccount


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**account_number** | **str** |  | [optional] 
**additional_email_addresses** | **str** |  | [optional] 
**allow_invoice_edit** | **bool** |  | [optional] 
**auto_pay** | **bool** |  | [optional] 
**balance** | **float** |  | [optional] 
**batch** | **str** |  | [optional] 
**bcd_setting_option** | **str** |  | [optional] 
**bill_cycle_day** | **int** |  | [optional] 
**bill_to_id** | **str** |  | [optional] 
**communication_profile_id** | **str** |  | [optional] 
**credit_balance** | **float** |  | [optional] 
**crm_id** | **str** |  | [optional] 
**currency** | **str** |  | [optional] 
**customer_service_rep_name** | **str** |  | [optional] 
**default_payment_method_id** | **str** |  | [optional] 
**e_invoice_profile_id** | **str** |  | [optional] 
**gateway_routing_eligible** | **bool** |  | [optional] 
**invoice_delivery_prefs_email** | **bool** |  | [optional] 
**invoice_delivery_prefs_print** | **bool** |  | [optional] 
**invoice_template_id** | **str** |  | [optional] 
**last_invoice_date** | **date** |  | [optional] 
**last_metrics_update** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**notes** | **str** |  | [optional] 
**organization_id** | **str** |  | [optional] 
**parent_id** | **str** |  | [optional] 
**partner_account** | **bool** |  | [optional] 
**payment_method_cascading_consent** | **bool** |  | [optional] 
**purchase_order_number** | **str** |  | [optional] 
**sales_rep_name** | **str** |  | [optional] 
**sequence_set_id** | **str** |  | [optional] 
**ship_to_id** | **str** |  | [optional] 
**sold_to_id** | **str** |  | [optional] 
**status** | **str** |  | [optional] 
**tax_company_code** | **str** |  | [optional] 
**tax_exempt_certificate_id** | **str** |  | [optional] 
**tax_exempt_certificate_type** | **str** |  | [optional] 
**tax_exempt_description** | **str** |  | [optional] 
**tax_exempt_effective_date** | **date** |  | [optional] 
**tax_exempt_entity_use_code** | **str** |  | [optional] 
**tax_exempt_expiration_date** | **date** |  | [optional] 
**tax_exempt_issuing_jurisdiction** | **str** |  | [optional] 
**tax_exempt_status** | **str** |  | [optional] 
**total_invoice_balance** | **float** |  | [optional] 
**unapplied_balance** | **float** |  | [optional] 
**v_atid** | **str** |  | [optional] 
**roll_up_usage** | **bool** |  | [optional] 
**mrr** | **float** |  | [optional] 
**total_debit_memo_balance** | **float** |  | [optional] 
**unapplied_credit_memo_amount** | **float** |  | [optional] 
**reserved_payment_amount** | **float** |  | [optional] 
**credit_memo_template_id** | **str** |  | [optional] 
**debit_memo_template_id** | **str** |  | [optional] 
**payment_gateway** | **str** |  | [optional] 
**payment_term** | **str** |  | [optional] 
**bill_to** | [**ExpandedContact**](ExpandedContact.md) |  | [optional] 
**sold_to** | [**ExpandedContact**](ExpandedContact.md) |  | [optional] 
**ship_to** | [**ExpandedContact**](ExpandedContact.md) |  | [optional] 
**default_payment_method** | [**ExpandedPaymentMethod**](ExpandedPaymentMethod.md) |  | [optional] 
**subscriptions** | [**List[ExpandedSubscription]**](ExpandedSubscription.md) |  | [optional] 
**payments** | [**List[ExpandedPayment]**](ExpandedPayment.md) |  | [optional] 
**refunds** | [**List[ExpandedRefund]**](ExpandedRefund.md) |  | [optional] 
**credit_memos** | [**List[ExpandedCreditMemo]**](ExpandedCreditMemo.md) |  | [optional] 
**debit_memos** | [**List[ExpandedDebitMemo]**](ExpandedDebitMemo.md) |  | [optional] 
**invoices** | [**List[ExpandedInvoice]**](ExpandedInvoice.md) |  | [optional] 
**usages** | [**List[ExpandedUsage]**](ExpandedUsage.md) |  | [optional] 
**payment_methods** | [**List[ExpandedPaymentMethod]**](ExpandedPaymentMethod.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_account import ExpandedAccount

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedAccount from a JSON string
expanded_account_instance = ExpandedAccount.from_json(json)
# print the JSON string representation of the object
print(ExpandedAccount.to_json())

# convert the object into a dict
expanded_account_dict = expanded_account_instance.to_dict()
# create an instance of ExpandedAccount from a dict
expanded_account_from_dict = ExpandedAccount.from_dict(expanded_account_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


