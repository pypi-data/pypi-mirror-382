# InvoiceItemsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully. | [optional] 
**invoice_items** | [**List[InvoiceItem]**](InvoiceItem.md) | Container for invoice items.  | [optional] 
**next_page** | **str** | URL to retrieve the next page of the response if it exists; otherwise absent. | [optional] 

## Example

```python
from zuora_sdk.models.invoice_items_response import InvoiceItemsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of InvoiceItemsResponse from a JSON string
invoice_items_response_instance = InvoiceItemsResponse.from_json(json)
# print the JSON string representation of the object
print(InvoiceItemsResponse.to_json())

# convert the object into a dict
invoice_items_response_dict = invoice_items_response_instance.to_dict()
# create an instance of InvoiceItemsResponse from a dict
invoice_items_response_from_dict = InvoiceItemsResponse.from_dict(invoice_items_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


