# BulkPostInvoicesRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**invoices** | [**List[PostInvoiceRequest]**](PostInvoiceRequest.md) | The container for invoices to be posted. The maximum number of invoices to be posted is 50 in one request. | [optional] 

## Example

```python
from zuora_sdk.models.bulk_post_invoices_request import BulkPostInvoicesRequest

# TODO update the JSON string below
json = "{}"
# create an instance of BulkPostInvoicesRequest from a JSON string
bulk_post_invoices_request_instance = BulkPostInvoicesRequest.from_json(json)
# print the JSON string representation of the object
print(BulkPostInvoicesRequest.to_json())

# convert the object into a dict
bulk_post_invoices_request_dict = bulk_post_invoices_request_instance.to_dict()
# create an instance of BulkPostInvoicesRequest from a dict
bulk_post_invoices_request_from_dict = BulkPostInvoicesRequest.from_dict(bulk_post_invoices_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


