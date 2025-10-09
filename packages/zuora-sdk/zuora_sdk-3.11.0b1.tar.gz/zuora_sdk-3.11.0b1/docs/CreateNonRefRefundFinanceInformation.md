# CreateNonRefRefundFinanceInformation

Container for the finance information related to the refund. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**bank_account_accounting_code** | **str** | The accounting code that maps to a bank account in your accounting system.  | [optional] 
**on_account_accounting_code** | **str** | The accounting code that maps to an on account in your accounting system.  | [optional] 
**transferred_to_accounting** | [**PostNonRefRefundTypeAllOfFinanceInformationTransferredToAccounting**](PostNonRefRefundTypeAllOfFinanceInformationTransferredToAccounting.md) |  | [optional] 
**unapplied_payment_accounting_code** | **str** | The accounting code for the unapplied payment.  | [optional] 

## Example

```python
from zuora_sdk.models.create_non_ref_refund_finance_information import CreateNonRefRefundFinanceInformation

# TODO update the JSON string below
json = "{}"
# create an instance of CreateNonRefRefundFinanceInformation from a JSON string
create_non_ref_refund_finance_information_instance = CreateNonRefRefundFinanceInformation.from_json(json)
# print the JSON string representation of the object
print(CreateNonRefRefundFinanceInformation.to_json())

# convert the object into a dict
create_non_ref_refund_finance_information_dict = create_non_ref_refund_finance_information_instance.to_dict()
# create an instance of CreateNonRefRefundFinanceInformation from a dict
create_non_ref_refund_finance_information_from_dict = CreateNonRefRefundFinanceInformation.from_dict(create_non_ref_refund_finance_information_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


