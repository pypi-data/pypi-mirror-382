# AccountSummaryPaymentInvoice


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**applied_payment_amount** | **decimal.Decimal** | Amount of payment applied to the invoice.  | [optional] 
**invoice_id** | **str** | Invoice ID.  | [optional] 
**invoice_number** | **str** | Invoice number.  | [optional] 

## Example

```python
from zuora_sdk.models.account_summary_payment_invoice import AccountSummaryPaymentInvoice

# TODO update the JSON string below
json = "{}"
# create an instance of AccountSummaryPaymentInvoice from a JSON string
account_summary_payment_invoice_instance = AccountSummaryPaymentInvoice.from_json(json)
# print the JSON string representation of the object
print(AccountSummaryPaymentInvoice.to_json())

# convert the object into a dict
account_summary_payment_invoice_dict = account_summary_payment_invoice_instance.to_dict()
# create an instance of AccountSummaryPaymentInvoice from a dict
account_summary_payment_invoice_from_dict = AccountSummaryPaymentInvoice.from_dict(account_summary_payment_invoice_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


