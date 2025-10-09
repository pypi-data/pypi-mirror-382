# GetCreditMemoPdfStatusBatchResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**credit_memo_files** | [**List[GetCreditMemoPdfStatusResponse]**](GetCreditMemoPdfStatusResponse.md) | Array of credit memo PDF statuses requested.  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] 

## Example

```python
from zuora_sdk.models.get_credit_memo_pdf_status_batch_response import GetCreditMemoPdfStatusBatchResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetCreditMemoPdfStatusBatchResponse from a JSON string
get_credit_memo_pdf_status_batch_response_instance = GetCreditMemoPdfStatusBatchResponse.from_json(json)
# print the JSON string representation of the object
print(GetCreditMemoPdfStatusBatchResponse.to_json())

# convert the object into a dict
get_credit_memo_pdf_status_batch_response_dict = get_credit_memo_pdf_status_batch_response_instance.to_dict()
# create an instance of GetCreditMemoPdfStatusBatchResponse from a dict
get_credit_memo_pdf_status_batch_response_from_dict = GetCreditMemoPdfStatusBatchResponse.from_dict(get_credit_memo_pdf_status_batch_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


