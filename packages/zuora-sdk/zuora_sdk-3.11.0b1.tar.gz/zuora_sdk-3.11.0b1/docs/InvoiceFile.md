# InvoiceFile


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the invoice PDF file. This is the ID for the file object and different from the file handle ID in the &#x60;pdfFileUrl&#x60; field. To open a file, you have to use the file handle ID. | [optional] 
**pdf_file_url** | **str** | The REST URL for the invoice PDF file. Click the URL to open the invoice PDF file. | [optional] 
**version_number** | **int** | The version number of the invoice PDF file.  | [optional] 

## Example

```python
from zuora_sdk.models.invoice_file import InvoiceFile

# TODO update the JSON string below
json = "{}"
# create an instance of InvoiceFile from a JSON string
invoice_file_instance = InvoiceFile.from_json(json)
# print the JSON string representation of the object
print(InvoiceFile.to_json())

# convert the object into a dict
invoice_file_dict = invoice_file_instance.to_dict()
# create an instance of InvoiceFile from a dict
invoice_file_from_dict = InvoiceFile.from_dict(invoice_file_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


