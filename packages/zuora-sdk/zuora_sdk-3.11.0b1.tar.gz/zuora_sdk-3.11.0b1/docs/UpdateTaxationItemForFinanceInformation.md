# UpdateTaxationItemForFinanceInformation

Container for the finance information related to the taxation item. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**accounts_receivable_accounting_code** | **str** | The accounting code for accounts receivable.  | [optional] 
**on_account_accounting_code** | **str** | The accounting code that maps to an on account in your accounting system.  | [optional] 
**sales_tax_payable_accounting_code** | **str** | The accounting code for the sales taxes payable.  | [optional] 

## Example

```python
from zuora_sdk.models.update_taxation_item_for_finance_information import UpdateTaxationItemForFinanceInformation

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateTaxationItemForFinanceInformation from a JSON string
update_taxation_item_for_finance_information_instance = UpdateTaxationItemForFinanceInformation.from_json(json)
# print the JSON string representation of the object
print(UpdateTaxationItemForFinanceInformation.to_json())

# convert the object into a dict
update_taxation_item_for_finance_information_dict = update_taxation_item_for_finance_information_instance.to_dict()
# create an instance of UpdateTaxationItemForFinanceInformation from a dict
update_taxation_item_for_finance_information_from_dict = UpdateTaxationItemForFinanceInformation.from_dict(update_taxation_item_for_finance_information_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


