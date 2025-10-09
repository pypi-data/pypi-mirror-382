# AsyncUnapplyCreditMemoRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**effective_date** | **date** | The date when the credit memo is unapplied.  | [optional] 
**invoices** | [**List[AsyncUnapplyCreditMemoToInvoice]**](AsyncUnapplyCreditMemoToInvoice.md) | Container for invoices that the credit memo is unapplied. The maximum number of invoices is 1,000. | [optional] 

## Example

```python
from zuora_sdk.models.async_unapply_credit_memo_request import AsyncUnapplyCreditMemoRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AsyncUnapplyCreditMemoRequest from a JSON string
async_unapply_credit_memo_request_instance = AsyncUnapplyCreditMemoRequest.from_json(json)
# print the JSON string representation of the object
print(AsyncUnapplyCreditMemoRequest.to_json())

# convert the object into a dict
async_unapply_credit_memo_request_dict = async_unapply_credit_memo_request_instance.to_dict()
# create an instance of AsyncUnapplyCreditMemoRequest from a dict
async_unapply_credit_memo_request_from_dict = AsyncUnapplyCreditMemoRequest.from_dict(async_unapply_credit_memo_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


