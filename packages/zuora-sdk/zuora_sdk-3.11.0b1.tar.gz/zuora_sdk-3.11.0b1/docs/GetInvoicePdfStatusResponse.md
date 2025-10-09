# GetInvoicePdfStatusResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**invoice_id** | **str** | The ID of the invoice whose pdf status is requested.  | [optional] 
**invoice_number** | **str** | The invoice number of the invoice whose pdf status is requested.  | [optional] 
**pdf_generation_status** | **str** | The generation status of the invoice PDF. Can be one of - None/Pending/Processing/Generated/Error/Obsolete/Archived  | [optional] 
**pdf_file_url** | **str** | The file URL of the invoice PDF if it&#39;s generated successfully.  | [optional] 
**error_category** | **str** | The error category if invoice PDF generation failed.  | [optional] 
**error_message** | **str** | The error message if invoice PDF generation failed.  | [optional] 
**created_on** | **str** | The time at which the request to generate the PDF was created.  | [optional] 
**updated_on** | **str** | The time at which the request to generate the PDF was updated.  | [optional] 

## Example

```python
from zuora_sdk.models.get_invoice_pdf_status_response import GetInvoicePdfStatusResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetInvoicePdfStatusResponse from a JSON string
get_invoice_pdf_status_response_instance = GetInvoicePdfStatusResponse.from_json(json)
# print the JSON string representation of the object
print(GetInvoicePdfStatusResponse.to_json())

# convert the object into a dict
get_invoice_pdf_status_response_dict = get_invoice_pdf_status_response_instance.to_dict()
# create an instance of GetInvoicePdfStatusResponse from a dict
get_invoice_pdf_status_response_from_dict = GetInvoicePdfStatusResponse.from_dict(get_invoice_pdf_status_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


