# EInvoicingFileFormat


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**b2_b** | **List[str]** | Specify the list of file formats that would be auto-downloaded while E-Invoice is in progress. List of supported file formats can be obtained from the mandates API under the specified business category B2B  | [optional] 
**b2_c** | **List[str]** | Specify the list of file formats that would be auto-downloaded while E-Invoice is in progress. List of supported file formats can be obtained from the mandates API under the specified business category B2C  | [optional] 
**b2_g** | **List[str]** | Specify the list of file formats that would be auto-downloaded while E-Invoice is in progress. List of supported file formats can be obtained from the mandates API under the specified business category B2G  | [optional] 

## Example

```python
from zuora_sdk.models.e_invoicing_file_format import EInvoicingFileFormat

# TODO update the JSON string below
json = "{}"
# create an instance of EInvoicingFileFormat from a JSON string
e_invoicing_file_format_instance = EInvoicingFileFormat.from_json(json)
# print the JSON string representation of the object
print(EInvoicingFileFormat.to_json())

# convert the object into a dict
e_invoicing_file_format_dict = e_invoicing_file_format_instance.to_dict()
# create an instance of EInvoicingFileFormat from a dict
e_invoicing_file_format_from_dict = EInvoicingFileFormat.from_dict(e_invoicing_file_format_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


