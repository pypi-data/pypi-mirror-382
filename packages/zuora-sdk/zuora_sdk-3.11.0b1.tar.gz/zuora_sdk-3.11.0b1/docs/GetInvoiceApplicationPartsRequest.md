# GetInvoiceApplicationPartsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**application_parts** | [**List[GetInvoiceApplicationPartRequest]**](GetInvoiceApplicationPartRequest.md) | Container for application parts.  | [optional] 
**next_page** | **str** | URL to retrieve the next page of the response if it exists; otherwise absent. | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully. | [optional] 

## Example

```python
from zuora_sdk.models.get_invoice_application_parts_request import GetInvoiceApplicationPartsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of GetInvoiceApplicationPartsRequest from a JSON string
get_invoice_application_parts_request_instance = GetInvoiceApplicationPartsRequest.from_json(json)
# print the JSON string representation of the object
print(GetInvoiceApplicationPartsRequest.to_json())

# convert the object into a dict
get_invoice_application_parts_request_dict = get_invoice_application_parts_request_instance.to_dict()
# create an instance of GetInvoiceApplicationPartsRequest from a dict
get_invoice_application_parts_request_from_dict = GetInvoiceApplicationPartsRequest.from_dict(get_invoice_application_parts_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


