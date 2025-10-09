# DebitMemoItemFromInvoiceItemFinanceInformation

Container for the finance information related to the debit memo item. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**deferred_revenue_accounting_code** | **str** | The accounting code for the deferred revenue, such as Monthly Recurring Liability. | [optional] 
**recognized_revenue_accounting_code** | **str** | The accounting code for the recognized revenue, such as Monthly Recurring Charges or Overage Charges. | [optional] 
**revenue_recognition_rule_name** | **str** | The name of the revenue recognition rule governing the revenue schedule.  | [optional] 

## Example

```python
from zuora_sdk.models.debit_memo_item_from_invoice_item_finance_information import DebitMemoItemFromInvoiceItemFinanceInformation

# TODO update the JSON string below
json = "{}"
# create an instance of DebitMemoItemFromInvoiceItemFinanceInformation from a JSON string
debit_memo_item_from_invoice_item_finance_information_instance = DebitMemoItemFromInvoiceItemFinanceInformation.from_json(json)
# print the JSON string representation of the object
print(DebitMemoItemFromInvoiceItemFinanceInformation.to_json())

# convert the object into a dict
debit_memo_item_from_invoice_item_finance_information_dict = debit_memo_item_from_invoice_item_finance_information_instance.to_dict()
# create an instance of DebitMemoItemFromInvoiceItemFinanceInformation from a dict
debit_memo_item_from_invoice_item_finance_information_from_dict = DebitMemoItemFromInvoiceItemFinanceInformation.from_dict(debit_memo_item_from_invoice_item_finance_information_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


