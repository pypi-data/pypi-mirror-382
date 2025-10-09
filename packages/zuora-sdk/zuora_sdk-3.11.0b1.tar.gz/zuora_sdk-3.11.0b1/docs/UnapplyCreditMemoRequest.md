# UnapplyCreditMemoRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**debit_memos** | [**List[UnapplyCreditMemoToDebitMemo]**](UnapplyCreditMemoToDebitMemo.md) | Container for debit memos that the credit memo is unapplied from. The maximum number of debit memos is 1,000. | [optional] 
**effective_date** | **date** | The date when the credit memo is unapplied.  | [optional] 
**invoices** | [**List[UnapplyCreditMemoToInvoice]**](UnapplyCreditMemoToInvoice.md) | Container for invoices that the credit memo is unapplied from. The maximum number of invoices is 1,000. | [optional] 

## Example

```python
from zuora_sdk.models.unapply_credit_memo_request import UnapplyCreditMemoRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UnapplyCreditMemoRequest from a JSON string
unapply_credit_memo_request_instance = UnapplyCreditMemoRequest.from_json(json)
# print the JSON string representation of the object
print(UnapplyCreditMemoRequest.to_json())

# convert the object into a dict
unapply_credit_memo_request_dict = unapply_credit_memo_request_instance.to_dict()
# create an instance of UnapplyCreditMemoRequest from a dict
unapply_credit_memo_request_from_dict = UnapplyCreditMemoRequest.from_dict(unapply_credit_memo_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


