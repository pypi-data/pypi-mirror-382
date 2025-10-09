# BulkUpdateInvoicesRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**invoices** | [**List[InvoiceForBulkUpdate]**](InvoiceForBulkUpdate.md) | Container for invoice update details.  | [optional] 

## Example

```python
from zuora_sdk.models.bulk_update_invoices_request import BulkUpdateInvoicesRequest

# TODO update the JSON string below
json = "{}"
# create an instance of BulkUpdateInvoicesRequest from a JSON string
bulk_update_invoices_request_instance = BulkUpdateInvoicesRequest.from_json(json)
# print the JSON string representation of the object
print(BulkUpdateInvoicesRequest.to_json())

# convert the object into a dict
bulk_update_invoices_request_dict = bulk_update_invoices_request_instance.to_dict()
# create an instance of BulkUpdateInvoicesRequest from a dict
bulk_update_invoices_request_from_dict = BulkUpdateInvoicesRequest.from_dict(bulk_update_invoices_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


