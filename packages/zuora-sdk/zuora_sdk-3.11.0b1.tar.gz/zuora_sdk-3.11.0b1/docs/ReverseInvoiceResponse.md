# ReverseInvoiceResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**credit_memo** | [**ReverseInvoiceResponseCreditMemo**](ReverseInvoiceResponseCreditMemo.md) |  | [optional] 
**debit_memo** | [**ReverseInvoiceResponseDebitMemo**](ReverseInvoiceResponseDebitMemo.md) |  | [optional] 
**id** | **str** | The ID of invoice | [optional] 
**job_id** | **str** | The ID of the operation job. | [optional] 
**job_status** | [**OperationJobStatus**](OperationJobStatus.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.reverse_invoice_response import ReverseInvoiceResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ReverseInvoiceResponse from a JSON string
reverse_invoice_response_instance = ReverseInvoiceResponse.from_json(json)
# print the JSON string representation of the object
print(ReverseInvoiceResponse.to_json())

# convert the object into a dict
reverse_invoice_response_dict = reverse_invoice_response_instance.to_dict()
# create an instance of ReverseInvoiceResponse from a dict
reverse_invoice_response_from_dict = ReverseInvoiceResponse.from_dict(reverse_invoice_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


