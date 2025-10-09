# ApplyCreditMemoRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**debit_memos** | [**List[ApplyCreditMemoToDebitMemo]**](ApplyCreditMemoToDebitMemo.md) | Container for debit memos that the credit memo is applied to. The maximum number of debit memos is 1,000. | [optional] 
**effective_date** | **date** | The date when the credit memo is applied.  | [optional] 
**invoices** | [**List[ApplyCreditMemoToInvoice]**](ApplyCreditMemoToInvoice.md) | Container for invoices that the credit memo is applied to. The maximum number of invoices is 1,000. | [optional] 

## Example

```python
from zuora_sdk.models.apply_credit_memo_request import ApplyCreditMemoRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ApplyCreditMemoRequest from a JSON string
apply_credit_memo_request_instance = ApplyCreditMemoRequest.from_json(json)
# print the JSON string representation of the object
print(ApplyCreditMemoRequest.to_json())

# convert the object into a dict
apply_credit_memo_request_dict = apply_credit_memo_request_instance.to_dict()
# create an instance of ApplyCreditMemoRequest from a dict
apply_credit_memo_request_from_dict = ApplyCreditMemoRequest.from_dict(apply_credit_memo_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


