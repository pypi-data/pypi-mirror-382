# CollectDebitMemoResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**applied_credit_memos** | [**List[CollectDebitMemoResponseAppliedCreditMemos]**](CollectDebitMemoResponseAppliedCreditMemos.md) | The information about which credit memo applied to the specific debit memo. | [optional] 
**applied_payments** | [**List[CollectDebitMemoResponseAppliedPayments]**](CollectDebitMemoResponseAppliedPayments.md) | The information about which payment applied to the specific debit memo. | [optional] 
**debit_memo** | [**CollectDebitMemoResponseDebitMemo**](CollectDebitMemoResponseDebitMemo.md) |  | [optional] 
**processed_payment** | [**CollectDebitMemoResponseProcessedPayment**](CollectDebitMemoResponseProcessedPayment.md) |  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully. | [optional] 

## Example

```python
from zuora_sdk.models.collect_debit_memo_response import CollectDebitMemoResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CollectDebitMemoResponse from a JSON string
collect_debit_memo_response_instance = CollectDebitMemoResponse.from_json(json)
# print the JSON string representation of the object
print(CollectDebitMemoResponse.to_json())

# convert the object into a dict
collect_debit_memo_response_dict = collect_debit_memo_response_instance.to_dict()
# create an instance of CollectDebitMemoResponse from a dict
collect_debit_memo_response_from_dict = CollectDebitMemoResponse.from_dict(collect_debit_memo_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


