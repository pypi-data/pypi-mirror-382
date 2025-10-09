# GetRefundCreditMemoFinanceInformation

Container for the finance information related to the refund. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**bank_account_accounting_code** | **str** | The accounting code that maps to a bank account in your accounting system.  | [optional] 
**bank_account_accounting_code_type** | **str** | The type of the accounting code that maps to a bank account in your accounting system.  | [optional] 
**transferred_to_accounting** | [**GetRefundCreditMemoTypeAllOfFinanceInformationTransferredToAccounting**](GetRefundCreditMemoTypeAllOfFinanceInformationTransferredToAccounting.md) |  | [optional] 
**unapplied_payment_accounting_code** | **str** | The accounting code for the unapplied payment.  | [optional] 
**unapplied_payment_accounting_code_type** | **str** | The type of the accounting code for the unapplied payment.  | [optional] 

## Example

```python
from zuora_sdk.models.get_refund_credit_memo_finance_information import GetRefundCreditMemoFinanceInformation

# TODO update the JSON string below
json = "{}"
# create an instance of GetRefundCreditMemoFinanceInformation from a JSON string
get_refund_credit_memo_finance_information_instance = GetRefundCreditMemoFinanceInformation.from_json(json)
# print the JSON string representation of the object
print(GetRefundCreditMemoFinanceInformation.to_json())

# convert the object into a dict
get_refund_credit_memo_finance_information_dict = get_refund_credit_memo_finance_information_instance.to_dict()
# create an instance of GetRefundCreditMemoFinanceInformation from a dict
get_refund_credit_memo_finance_information_from_dict = GetRefundCreditMemoFinanceInformation.from_dict(get_refund_credit_memo_finance_information_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


