# InvoicePostResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the invoice was posted successfully.  | [optional] 
**id** | **str** | The ID of the invoice that was posted.  | [optional] 

## Example

```python
from zuora_sdk.models.invoice_post_response import InvoicePostResponse

# TODO update the JSON string below
json = "{}"
# create an instance of InvoicePostResponse from a JSON string
invoice_post_response_instance = InvoicePostResponse.from_json(json)
# print the JSON string representation of the object
print(InvoicePostResponse.to_json())

# convert the object into a dict
invoice_post_response_dict = invoice_post_response_instance.to_dict()
# create an instance of InvoicePostResponse from a dict
invoice_post_response_from_dict = InvoicePostResponse.from_dict(invoice_post_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


