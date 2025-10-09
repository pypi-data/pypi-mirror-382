# PostInvoiceRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the invoice to be posted.  | [optional] 
**invoice_date** | **date** | The date that appears on the invoice being created, in &#x60;yyyy-mm-dd&#x60; format. The value cannot fall in a closed accounting period.  | [optional] 

## Example

```python
from zuora_sdk.models.post_invoice_request import PostInvoiceRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PostInvoiceRequest from a JSON string
post_invoice_request_instance = PostInvoiceRequest.from_json(json)
# print the JSON string representation of the object
print(PostInvoiceRequest.to_json())

# convert the object into a dict
post_invoice_request_dict = post_invoice_request_instance.to_dict()
# create an instance of PostInvoiceRequest from a dict
post_invoice_request_from_dict = PostInvoiceRequest.from_dict(post_invoice_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


