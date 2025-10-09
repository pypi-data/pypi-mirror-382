# PaymentRequestFinanceInformation

Container for the finance information related to the payment. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**bank_account_accounting_code** | **str** | The accounting code that maps to a bank account in your accounting system.  | [optional] 
**transferred_to_accounting** | [**PaymentFinanceInformationTransferredToAccounting**](PaymentFinanceInformationTransferredToAccounting.md) |  | [optional] 
**unapplied_payment_accounting_code** | **str** | The accounting code for the unapplied payment.  | [optional] 

## Example

```python
from zuora_sdk.models.payment_request_finance_information import PaymentRequestFinanceInformation

# TODO update the JSON string below
json = "{}"
# create an instance of PaymentRequestFinanceInformation from a JSON string
payment_request_finance_information_instance = PaymentRequestFinanceInformation.from_json(json)
# print the JSON string representation of the object
print(PaymentRequestFinanceInformation.to_json())

# convert the object into a dict
payment_request_finance_information_dict = payment_request_finance_information_instance.to_dict()
# create an instance of PaymentRequestFinanceInformation from a dict
payment_request_finance_information_from_dict = PaymentRequestFinanceInformation.from_dict(payment_request_finance_information_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


