# UpdateCreditMemoTaxItemFinanceInformation

Container for the finance information related to the taxation item in the credit memo item.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**on_account_accounting_code** | **str** | The accounting code that maps to an on account in your accounting system.  | [optional] 
**sales_tax_payable_accounting_code** | **str** | The accounting code for the sales taxes payable.  | [optional] 

## Example

```python
from zuora_sdk.models.update_credit_memo_tax_item_finance_information import UpdateCreditMemoTaxItemFinanceInformation

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateCreditMemoTaxItemFinanceInformation from a JSON string
update_credit_memo_tax_item_finance_information_instance = UpdateCreditMemoTaxItemFinanceInformation.from_json(json)
# print the JSON string representation of the object
print(UpdateCreditMemoTaxItemFinanceInformation.to_json())

# convert the object into a dict
update_credit_memo_tax_item_finance_information_dict = update_credit_memo_tax_item_finance_information_instance.to_dict()
# create an instance of UpdateCreditMemoTaxItemFinanceInformation from a dict
update_credit_memo_tax_item_finance_information_from_dict = UpdateCreditMemoTaxItemFinanceInformation.from_dict(update_credit_memo_tax_item_finance_information_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


