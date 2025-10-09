# CreateTaxationItemForCreditMemoFinanceInformation

Container for the finance information related to the taxation item. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**on_account_accounting_code** | **str** | The accounting code that maps to an on account in your accounting system.  | [optional] 
**sales_tax_payable_accounting_code** | **str** | The accounting code for the sales taxes payable.  | [optional] 

## Example

```python
from zuora_sdk.models.create_taxation_item_for_credit_memo_finance_information import CreateTaxationItemForCreditMemoFinanceInformation

# TODO update the JSON string below
json = "{}"
# create an instance of CreateTaxationItemForCreditMemoFinanceInformation from a JSON string
create_taxation_item_for_credit_memo_finance_information_instance = CreateTaxationItemForCreditMemoFinanceInformation.from_json(json)
# print the JSON string representation of the object
print(CreateTaxationItemForCreditMemoFinanceInformation.to_json())

# convert the object into a dict
create_taxation_item_for_credit_memo_finance_information_dict = create_taxation_item_for_credit_memo_finance_information_instance.to_dict()
# create an instance of CreateTaxationItemForCreditMemoFinanceInformation from a dict
create_taxation_item_for_credit_memo_finance_information_from_dict = CreateTaxationItemForCreditMemoFinanceInformation.from_dict(create_taxation_item_for_credit_memo_finance_information_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


