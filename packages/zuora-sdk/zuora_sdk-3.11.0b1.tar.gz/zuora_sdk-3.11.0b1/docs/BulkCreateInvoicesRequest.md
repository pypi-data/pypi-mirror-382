# BulkCreateInvoicesRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**invoices** | [**List[CreateInvoiceRequest]**](CreateInvoiceRequest.md) | Container for standalone invoices.  | [optional] 
**use_single_transaction** | **bool** | Whether a batch request is handled with a single transaction.   - &#x60;true&#x60; indicates that a batch request will be handled with a single transaction.  - &#x60;false&#x60;  indicates that the standalone invoices to be created in a batch request will be handled with separated transactions.   If the field is set to &#x60;false&#x60;, a failure in the batch request will not cause the whole request to fail, so you have to retry the whole batch request. | [optional] 

## Example

```python
from zuora_sdk.models.bulk_create_invoices_request import BulkCreateInvoicesRequest

# TODO update the JSON string below
json = "{}"
# create an instance of BulkCreateInvoicesRequest from a JSON string
bulk_create_invoices_request_instance = BulkCreateInvoicesRequest.from_json(json)
# print the JSON string representation of the object
print(BulkCreateInvoicesRequest.to_json())

# convert the object into a dict
bulk_create_invoices_request_dict = bulk_create_invoices_request_instance.to_dict()
# create an instance of BulkCreateInvoicesRequest from a dict
bulk_create_invoices_request_from_dict = BulkCreateInvoicesRequest.from_dict(bulk_create_invoices_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


