# CreditMemoItemFinanceInformation

Container for the finance information related to the credit memo item. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**deferred_revenue_accounting_code** | **str** | The accounting code for the deferred revenue, such as Monthly Recurring Liability. | [optional] 
**deferred_revenue_accounting_code_type** | **str** | The type of the deferred revenue accounting code, such as Deferred Revenue.  | [optional] 
**on_account_accounting_code** | **str** | The accounting code that maps to an on account in your accounting system.  | [optional] 
**on_account_accounting_code_type** | **str** | The type of the accounting code that maps to an on account in your accounting system. | [optional] 
**recognized_revenue_accounting_code** | **str** | The accounting code for the recognized revenue, such as Monthly Recurring Charges or Overage Charges. | [optional] 
**non_revenue_write_off_accounting_code_type** | **str** | The type of the Non Revenue write-off accounting code, such as Bad Debt | [optional] 
**non_revenue_write_off_accounting_code** | **str** | The accounting code for the Non Revenue write-off accounting code, such as Bank Fee. | [optional] 
**recognized_revenue_accounting_code_type** | **str** | The type of the recognized revenue accounting code, such as Sales Revenue or Sales Discount.  | [optional] 
**revenue_recognition_rule_name** | **str** | The name of the revenue recognition rule governing the revenue schedule.  | [optional] 
**revenue_schedule_number** | **str** | Revenue schedule number. The revenue schedule number is always prefixed with \&quot;RS\&quot;, for example, RS-00000001. | [optional] 

## Example

```python
from zuora_sdk.models.credit_memo_item_finance_information import CreditMemoItemFinanceInformation

# TODO update the JSON string below
json = "{}"
# create an instance of CreditMemoItemFinanceInformation from a JSON string
credit_memo_item_finance_information_instance = CreditMemoItemFinanceInformation.from_json(json)
# print the JSON string representation of the object
print(CreditMemoItemFinanceInformation.to_json())

# convert the object into a dict
credit_memo_item_finance_information_dict = credit_memo_item_finance_information_instance.to_dict()
# create an instance of CreditMemoItemFinanceInformation from a dict
credit_memo_item_finance_information_from_dict = CreditMemoItemFinanceInformation.from_dict(credit_memo_item_finance_information_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


