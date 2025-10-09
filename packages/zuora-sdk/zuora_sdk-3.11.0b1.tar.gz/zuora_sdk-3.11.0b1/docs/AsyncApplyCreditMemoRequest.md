# AsyncApplyCreditMemoRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**effective_date** | **date** | The date when the credit memo is applied.  | [optional] 
**invoices** | [**List[AsyncApplyCreditMemoToInvoice]**](AsyncApplyCreditMemoToInvoice.md) | Container for invoices that the credit memo is applied to. The maximum number of invoices is 1,000. | [optional] 

## Example

```python
from zuora_sdk.models.async_apply_credit_memo_request import AsyncApplyCreditMemoRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AsyncApplyCreditMemoRequest from a JSON string
async_apply_credit_memo_request_instance = AsyncApplyCreditMemoRequest.from_json(json)
# print the JSON string representation of the object
print(AsyncApplyCreditMemoRequest.to_json())

# convert the object into a dict
async_apply_credit_memo_request_dict = async_apply_credit_memo_request_instance.to_dict()
# create an instance of AsyncApplyCreditMemoRequest from a dict
async_apply_credit_memo_request_from_dict = AsyncApplyCreditMemoRequest.from_dict(async_apply_credit_memo_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


