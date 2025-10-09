# GetInvoicePdfStatusBatchResponse



## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**invoice_files** | [**List[GetInvoicePdfStatusResponse]**](GetInvoicePdfStatusResponse.md) | Array of invoice PDF statuses requested.  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] 

## Example

```python
from zuora_sdk.models.get_invoice_pdf_status_batch_response import GetInvoicePdfStatusBatchResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetInvoicePdfStatusBatchResponse from a JSON string
get_invoice_pdf_status_batch_response_instance = GetInvoicePdfStatusBatchResponse.from_json(json)
# print the JSON string representation of the object
print(GetInvoicePdfStatusBatchResponse.to_json())

# convert the object into a dict
get_invoice_pdf_status_batch_response_dict = get_invoice_pdf_status_batch_response_instance.to_dict()
# create an instance of GetInvoicePdfStatusBatchResponse from a dict
get_invoice_pdf_status_batch_response_from_dict = GetInvoicePdfStatusBatchResponse.from_dict(get_invoice_pdf_status_batch_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


