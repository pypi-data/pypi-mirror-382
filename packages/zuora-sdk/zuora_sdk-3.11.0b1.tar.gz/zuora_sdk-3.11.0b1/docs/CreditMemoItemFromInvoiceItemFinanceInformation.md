# CreditMemoItemFromInvoiceItemFinanceInformation

Container for the finance information related to the credit memo item. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**deferred_revenue_accounting_code** | **str** | The accounting code for the deferred revenue, such as Monthly Recurring Liability. | [optional] 
**on_account_accounting_code** | **str** | The accounting code that maps to an on account in your accounting system.  | [optional] 
**recognized_revenue_accounting_code** | **str** | The accounting code for the recognized revenue, such as Monthly Recurring Charges or Overage Charges. | [optional] 
**revenue_recognition_rule_name** | **str** | The name of the revenue recognition rule governing the revenue schedule.  | [optional] 

## Example

```python
from zuora_sdk.models.credit_memo_item_from_invoice_item_finance_information import CreditMemoItemFromInvoiceItemFinanceInformation

# TODO update the JSON string below
json = "{}"
# create an instance of CreditMemoItemFromInvoiceItemFinanceInformation from a JSON string
credit_memo_item_from_invoice_item_finance_information_instance = CreditMemoItemFromInvoiceItemFinanceInformation.from_json(json)
# print the JSON string representation of the object
print(CreditMemoItemFromInvoiceItemFinanceInformation.to_json())

# convert the object into a dict
credit_memo_item_from_invoice_item_finance_information_dict = credit_memo_item_from_invoice_item_finance_information_instance.to_dict()
# create an instance of CreditMemoItemFromInvoiceItemFinanceInformation from a dict
credit_memo_item_from_invoice_item_finance_information_from_dict = CreditMemoItemFromInvoiceItemFinanceInformation.from_dict(credit_memo_item_from_invoice_item_finance_information_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


