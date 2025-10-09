# CreditMemoItemFromChargeDetailFinanceInformation

Container for the finance information related to the product rate plan charge associated with the credit memo.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**deferred_revenue_accounting_code** | **str** | The accounting code for the deferred revenue, such as Monthly Recurring Liability. | [optional] 
**on_account_accounting_code** | **str** | The accounting code that maps to an on account in your accounting system.  | [optional] 
**recognized_revenue_accounting_code** | **str** | The accounting code for the recognized revenue, such as Monthly Recurring Charges or Overage Charges. | [optional] 
**revenue_recognition_rule_name** | **str** | The name of the revenue recognition rule governing the revenue schedule.  | [optional] 

## Example

```python
from zuora_sdk.models.credit_memo_item_from_charge_detail_finance_information import CreditMemoItemFromChargeDetailFinanceInformation

# TODO update the JSON string below
json = "{}"
# create an instance of CreditMemoItemFromChargeDetailFinanceInformation from a JSON string
credit_memo_item_from_charge_detail_finance_information_instance = CreditMemoItemFromChargeDetailFinanceInformation.from_json(json)
# print the JSON string representation of the object
print(CreditMemoItemFromChargeDetailFinanceInformation.to_json())

# convert the object into a dict
credit_memo_item_from_charge_detail_finance_information_dict = credit_memo_item_from_charge_detail_finance_information_instance.to_dict()
# create an instance of CreditMemoItemFromChargeDetailFinanceInformation from a dict
credit_memo_item_from_charge_detail_finance_information_from_dict = CreditMemoItemFromChargeDetailFinanceInformation.from_dict(credit_memo_item_from_charge_detail_finance_information_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


