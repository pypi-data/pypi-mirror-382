# GetDebitMemoPdfStatusBatchResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**debit_memo_files** | [**List[GetDebitMemoPdfStatusResponse]**](GetDebitMemoPdfStatusResponse.md) | Array of debit memo PDF statuses requested.  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] 

## Example

```python
from zuora_sdk.models.get_debit_memo_pdf_status_batch_response import GetDebitMemoPdfStatusBatchResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetDebitMemoPdfStatusBatchResponse from a JSON string
get_debit_memo_pdf_status_batch_response_instance = GetDebitMemoPdfStatusBatchResponse.from_json(json)
# print the JSON string representation of the object
print(GetDebitMemoPdfStatusBatchResponse.to_json())

# convert the object into a dict
get_debit_memo_pdf_status_batch_response_dict = get_debit_memo_pdf_status_batch_response_instance.to_dict()
# create an instance of GetDebitMemoPdfStatusBatchResponse from a dict
get_debit_memo_pdf_status_batch_response_from_dict = GetDebitMemoPdfStatusBatchResponse.from_dict(get_debit_memo_pdf_status_batch_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


