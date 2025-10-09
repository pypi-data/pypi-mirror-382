# GetCreditMemoTaxItemFinanceInformation

Container for the finance information related to the taxation item. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**on_account_accounting_code** | **str** | The accounting code that maps to an on account in your accounting system.  | [optional] 
**on_account_accounting_code_type** | **str** | The type of the accounting code that maps to an on account in your accounting system. | [optional] 
**sales_tax_payable_accounting_code** | **str** | The accounting code for the sales taxes payable.  | [optional] 
**sales_tax_payable_accounting_code_type** | **str** | The type of the accounting code for the sales taxes payable.  | [optional] 

## Example

```python
from zuora_sdk.models.get_credit_memo_tax_item_finance_information import GetCreditMemoTaxItemFinanceInformation

# TODO update the JSON string below
json = "{}"
# create an instance of GetCreditMemoTaxItemFinanceInformation from a JSON string
get_credit_memo_tax_item_finance_information_instance = GetCreditMemoTaxItemFinanceInformation.from_json(json)
# print the JSON string representation of the object
print(GetCreditMemoTaxItemFinanceInformation.to_json())

# convert the object into a dict
get_credit_memo_tax_item_finance_information_dict = get_credit_memo_tax_item_finance_information_instance.to_dict()
# create an instance of GetCreditMemoTaxItemFinanceInformation from a dict
get_credit_memo_tax_item_finance_information_from_dict = GetCreditMemoTaxItemFinanceInformation.from_dict(get_credit_memo_tax_item_finance_information_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


