# CreatePaymentRunData


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_id** | **str** | A valid account ID associated with the payment run.  If &#x60;consolidatedPayment&#x60; is set to &#x60;true&#x60;, this field is used in processing a single payment for invoices/debit memos due on an account.  | [optional] 
**account_number** | **str** | The number of the customer account associated with the payment run, such as &#x60;A00000001&#x60;.  You can specify either &#x60;accountNumber&#x60; or &#x60;accountId&#x60; for a customer account, but not both of them.  If &#x60;consolidatedPayment&#x60; is set to &#x60;true&#x60;, this field is used in processing a single payment for invoices, debit memos, and standalone payments due on an account.  | [optional] 
**amount** | **float** | The amount to be collected for the specified invoice/debit memo. &#x60;amount&#x60; must be a positive numeric value no more than the balance of the specified invoice/debit memo.  This field is only available when &#x60;documentId&#x60; is specified. If &#x60;amount&#x60; is not specified, whole balance of the invoice/debit memo is collected.  | [optional] 
**comment** | **str** | Additional comments.  | [optional] 
**currency** | **str** | Note: This field is only available if support for standalone payments is enabled.  The currency of the standalone payment. Specify this field only if the &#x60;standalone&#x60; field is &#x60;true&#x60;. The currency of the standalone payment can be different from the payment currency defined in the customer account settings.  | [optional] 
**document_id** | **str** | The ID of a billing document associated with the payment run. &#x60;documentId&#x60; must be valid and match with &#x60;documentType&#x60;.  You must either specify both &#x60;documentId&#x60; and &#x60;documentType&#x60;, or specify neither of them.  If neither of &#x60;documentType&#x60; and &#x60;documentId&#x60; is specified, all invoices/debit memos with open balance of the account are collected.  | [optional] 
**document_number** | **str** | The number of a billing document associated with the payment run. &#x60;documentNumber&#x60; must be valid and match with &#x60;documentType&#x60;.  You must either specify both &#x60;documentNumber&#x60; and &#x60;documentType&#x60;, or specify neither of them.  If neither of &#x60;documentType&#x60; and &#x60;documentNumber&#x60; is specified, all invoices/debit memos with open balance of the account are collected.  | [optional] 
**document_type** | **str** | The type of a billing document associated with the payment run. The value can be &#x60;Invoice&#x60; or &#x60;DebitMemo&#x60;, but &#x60;DebitMemo&#x60; is only supported if the Invoice Settlement feature is enabled.  You must either specify both &#x60;documentType&#x60; and &#x60;documentId&#x60;, or specify neither of them.  If neither of &#x60;documentType&#x60; and &#x60;documentId&#x60; is specified, all invoices/debit memos with open balance of the account are collected.  | [optional] 
**payment_gateway_id** | **str** | The ID of the payment gateway for collecting invoices/debit memos. The specified payment gateway must be valid and active. If it is not specified, the default payment gateway of the account is used. If no payment gateway is configured for the account, the default payment gateway of the tenant is used.  If &#x60;consolidatedPayment&#x60; is set to &#x60;true&#x60;, this field is used in processing a single payment for invoices/debit memos due on an account.  | [optional] 
**payment_method_id** | **str** | The ID of the payment method for collecting invoices/debit memos. The specified payment method must be a valid non-system payment method. If it is not specified, the default payment method of the account is used regardless of the &#x60;autoPay&#x60; value of the account.  If &#x60;processPaymentWithClosedPM&#x60; is set to &#x60;false&#x60;, the payment method cannot be closed.  If the payment retry rules are enabled, the payment method must meet the rules.  If &#x60;consolidatedPayment&#x60; is set to &#x60;true&#x60;, this field is used in processing a single payment for invoices/debit memos due on an account.  | [optional] 
**standalone** | **bool** | Note: This field is only available if support for standalone payments is enabled.  Specify &#x60;true&#x60; to indicate that this is a standalone payment that will be created and processed in Zuora through Zuora gateway integration but will be settled outside of Zuora. When &#x60;standalone&#x60; is set to &#x60;true&#x60;:  - &#x60;accountId&#x60; or &#x60;accountNumber&#x60; is required.   - &#x60;amount&#x60; is required.    - The amount will not be summed up into the account balance and key metrics regardless of the payment currency.   - No settlement data will be created.   - Either the applied amount or the unapplied amount of the payment is zero.   - The standalone payment cannot be applied, unapplied, or transferred.  | [optional] 
**data_items** | [**List[CreatePaymentRunDataItem]**](CreatePaymentRunDataItem.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.create_payment_run_data import CreatePaymentRunData

# TODO update the JSON string below
json = "{}"
# create an instance of CreatePaymentRunData from a JSON string
create_payment_run_data_instance = CreatePaymentRunData.from_json(json)
# print the JSON string representation of the object
print(CreatePaymentRunData.to_json())

# convert the object into a dict
create_payment_run_data_dict = create_payment_run_data_instance.to_dict()
# create an instance of CreatePaymentRunData from a dict
create_payment_run_data_from_dict = CreatePaymentRunData.from_dict(create_payment_run_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


