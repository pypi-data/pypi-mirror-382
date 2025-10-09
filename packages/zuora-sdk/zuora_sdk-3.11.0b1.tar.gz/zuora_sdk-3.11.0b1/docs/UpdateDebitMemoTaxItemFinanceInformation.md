# UpdateDebitMemoTaxItemFinanceInformation

Container for the finance information related to the taxation item in the debit memo item.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sales_tax_payable_accounting_code** | **str** | The accounting code for the sales taxes payable.  | [optional] 

## Example

```python
from zuora_sdk.models.update_debit_memo_tax_item_finance_information import UpdateDebitMemoTaxItemFinanceInformation

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateDebitMemoTaxItemFinanceInformation from a JSON string
update_debit_memo_tax_item_finance_information_instance = UpdateDebitMemoTaxItemFinanceInformation.from_json(json)
# print the JSON string representation of the object
print(UpdateDebitMemoTaxItemFinanceInformation.to_json())

# convert the object into a dict
update_debit_memo_tax_item_finance_information_dict = update_debit_memo_tax_item_finance_information_instance.to_dict()
# create an instance of UpdateDebitMemoTaxItemFinanceInformation from a dict
update_debit_memo_tax_item_finance_information_from_dict = UpdateDebitMemoTaxItemFinanceInformation.from_dict(update_debit_memo_tax_item_finance_information_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


