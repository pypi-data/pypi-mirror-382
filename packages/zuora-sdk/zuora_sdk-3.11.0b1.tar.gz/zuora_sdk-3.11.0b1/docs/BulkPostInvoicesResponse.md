# BulkPostInvoicesResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**invoices** | [**List[InvoicePostResponse]**](InvoicePostResponse.md) | The container for a list of posted invoices.  | [optional] 

## Example

```python
from zuora_sdk.models.bulk_post_invoices_response import BulkPostInvoicesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of BulkPostInvoicesResponse from a JSON string
bulk_post_invoices_response_instance = BulkPostInvoicesResponse.from_json(json)
# print the JSON string representation of the object
print(BulkPostInvoicesResponse.to_json())

# convert the object into a dict
bulk_post_invoices_response_dict = bulk_post_invoices_response_instance.to_dict()
# create an instance of BulkPostInvoicesResponse from a dict
bulk_post_invoices_response_from_dict = BulkPostInvoicesResponse.from_dict(bulk_post_invoices_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


