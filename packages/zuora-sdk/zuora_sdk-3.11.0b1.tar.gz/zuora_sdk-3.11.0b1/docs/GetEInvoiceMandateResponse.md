# GetEInvoiceMandateResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**country_code** | **str** | The two-letter ISO 3166-1 alpha-2 country code that the business region of the document belongs to. | [optional] 
**file_formats** | **List[str]** | A list of supported downloadable file formats for the given input mandate. | [optional] 
**category** | [**BusinessCategory**](BusinessCategory.md) |  | [optional] 
**process_type** | [**EInvoiceProcessType**](EInvoiceProcessType.md) |  | [optional] 
**default_file_formats** | **List[str]** | Default list of file formats selected when configuring the business region. | [optional] 

## Example

```python
from zuora_sdk.models.get_e_invoice_mandate_response import GetEInvoiceMandateResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetEInvoiceMandateResponse from a JSON string
get_e_invoice_mandate_response_instance = GetEInvoiceMandateResponse.from_json(json)
# print the JSON string representation of the object
print(GetEInvoiceMandateResponse.to_json())

# convert the object into a dict
get_e_invoice_mandate_response_dict = get_e_invoice_mandate_response_instance.to_dict()
# create an instance of GetEInvoiceMandateResponse from a dict
get_e_invoice_mandate_response_from_dict = GetEInvoiceMandateResponse.from_dict(get_e_invoice_mandate_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


