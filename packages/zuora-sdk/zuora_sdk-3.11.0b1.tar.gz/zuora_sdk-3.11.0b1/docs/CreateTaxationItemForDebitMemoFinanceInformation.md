# CreateTaxationItemForDebitMemoFinanceInformation

Container for the finance information related to the taxation item. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sales_tax_payable_accounting_code** | **str** | The accounting code for the sales taxes payable.  | [optional] 

## Example

```python
from zuora_sdk.models.create_taxation_item_for_debit_memo_finance_information import CreateTaxationItemForDebitMemoFinanceInformation

# TODO update the JSON string below
json = "{}"
# create an instance of CreateTaxationItemForDebitMemoFinanceInformation from a JSON string
create_taxation_item_for_debit_memo_finance_information_instance = CreateTaxationItemForDebitMemoFinanceInformation.from_json(json)
# print the JSON string representation of the object
print(CreateTaxationItemForDebitMemoFinanceInformation.to_json())

# convert the object into a dict
create_taxation_item_for_debit_memo_finance_information_dict = create_taxation_item_for_debit_memo_finance_information_instance.to_dict()
# create an instance of CreateTaxationItemForDebitMemoFinanceInformation from a dict
create_taxation_item_for_debit_memo_finance_information_from_dict = CreateTaxationItemForDebitMemoFinanceInformation.from_dict(create_taxation_item_for_debit_memo_finance_information_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


