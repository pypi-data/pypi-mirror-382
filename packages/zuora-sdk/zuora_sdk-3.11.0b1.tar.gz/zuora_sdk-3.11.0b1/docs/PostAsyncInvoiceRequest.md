# PostAsyncInvoiceRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**invoice_date** | **date** | The new invoice date when posting the invoice. By default, it will use invoice date of the invoice. | [optional] 

## Example

```python
from zuora_sdk.models.post_async_invoice_request import PostAsyncInvoiceRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PostAsyncInvoiceRequest from a JSON string
post_async_invoice_request_instance = PostAsyncInvoiceRequest.from_json(json)
# print the JSON string representation of the object
print(PostAsyncInvoiceRequest.to_json())

# convert the object into a dict
post_async_invoice_request_dict = post_async_invoice_request_instance.to_dict()
# create an instance of PostAsyncInvoiceRequest from a dict
post_async_invoice_request_from_dict = PostAsyncInvoiceRequest.from_dict(post_async_invoice_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


