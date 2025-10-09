# TaxationItemFinanceInformation

Container for the finance information related to the taxation item. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**accounts_receivable_accounting_code** | **str** | The accounting code for accounts receivable.  | [optional] 
**accounts_receivable_accounting_code_type** | **str** | The type of the accounting code for accounts receivable.  | [optional] 
**on_account_accounting_code** | **str** | The accounting code for account.  | [optional] 
**on_account_accounting_code_type** | **str** | The type of the accounting code for account.  | [optional] 
**sales_tax_payable_accounting_code** | **str** | The accounting code for the sales taxes payable.  | [optional] 
**sales_tax_payable_accounting_code_type** | **str** | The type of the accounting code for the sales taxes payable.  | [optional] 

## Example

```python
from zuora_sdk.models.taxation_item_finance_information import TaxationItemFinanceInformation

# TODO update the JSON string below
json = "{}"
# create an instance of TaxationItemFinanceInformation from a JSON string
taxation_item_finance_information_instance = TaxationItemFinanceInformation.from_json(json)
# print the JSON string representation of the object
print(TaxationItemFinanceInformation.to_json())

# convert the object into a dict
taxation_item_finance_information_dict = taxation_item_finance_information_instance.to_dict()
# create an instance of TaxationItemFinanceInformation from a dict
taxation_item_finance_information_from_dict = TaxationItemFinanceInformation.from_dict(taxation_item_finance_information_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


