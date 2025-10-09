# RefundRequestFinanceInformation

Container for the finance information related to the refund. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**bank_account_accounting_code** | **str** | The accounting code that maps to a bank account in your accounting system.  | [optional] 
**transferred_to_accounting** | [**RefundFinanceInformationTransferredToAccounting**](RefundFinanceInformationTransferredToAccounting.md) |  | [optional] 
**unapplied_payment_accounting_code** | **str** | The accounting code for the unapplied payment.  | [optional] 

## Example

```python
from zuora_sdk.models.refund_request_finance_information import RefundRequestFinanceInformation

# TODO update the JSON string below
json = "{}"
# create an instance of RefundRequestFinanceInformation from a JSON string
refund_request_finance_information_instance = RefundRequestFinanceInformation.from_json(json)
# print the JSON string representation of the object
print(RefundRequestFinanceInformation.to_json())

# convert the object into a dict
refund_request_finance_information_dict = refund_request_finance_information_instance.to_dict()
# create an instance of RefundRequestFinanceInformation from a dict
refund_request_finance_information_from_dict = RefundRequestFinanceInformation.from_dict(refund_request_finance_information_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


