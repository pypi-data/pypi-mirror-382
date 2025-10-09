# GetDebitMemoItemFinanceInformation

Container for the finance information related to the debit memo item. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**deferred_revenue_accounting_code** | **str** | The accounting code for the deferred revenue, such as Monthly Recurring Liability. | [optional] 
**deferred_revenue_accounting_code_type** | **str** | The type of the deferred revenue accounting code, such as Deferred Revenue. | [optional] 
**recognized_revenue_accounting_code** | **str** | The accounting code for the recognized revenue, such as Monthly Recurring Charges or Overage Charges. | [optional] 
**recognized_revenue_accounting_code_type** | **str** | The type of the recognized revenue accounting code, such as Sales Revenue or Sales Discount. | [optional] 
**revenue_recognition_rule_name** | **str** | The name of the revenue recognition rule governing the revenue schedule.  | [optional] 
**revenue_schedule_number** | **str** | The revenue schedule number. The revenue schedule number is always prefixed with \&quot;RS\&quot;, for example, RS-00000001. | [optional] 

## Example

```python
from zuora_sdk.models.get_debit_memo_item_finance_information import GetDebitMemoItemFinanceInformation

# TODO update the JSON string below
json = "{}"
# create an instance of GetDebitMemoItemFinanceInformation from a JSON string
get_debit_memo_item_finance_information_instance = GetDebitMemoItemFinanceInformation.from_json(json)
# print the JSON string representation of the object
print(GetDebitMemoItemFinanceInformation.to_json())

# convert the object into a dict
get_debit_memo_item_finance_information_dict = get_debit_memo_item_finance_information_instance.to_dict()
# create an instance of GetDebitMemoItemFinanceInformation from a dict
get_debit_memo_item_finance_information_from_dict = GetDebitMemoItemFinanceInformation.from_dict(get_debit_memo_item_finance_information_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


