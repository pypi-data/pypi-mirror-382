# InvoiceSettlementAsyncJobResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**id** | **str** | The ID of the operation job. | [optional] 
**status** | [**InvoiceSettlementAsyncJobStatus**](InvoiceSettlementAsyncJobStatus.md) |  | [optional] 
**operation_type** | [**InvoiceSettlementAsyncJobOperationType**](InvoiceSettlementAsyncJobOperationType.md) |  | [optional] 
**reference_id** | **str** | The ID of the business object which is being operated. | [optional] 
**reference_type** | [**InvoiceSettlementAsyncJobReferenceType**](InvoiceSettlementAsyncJobReferenceType.md) |  | [optional] 
**error** | **str** | The error message if the operation error out. | [optional] 

## Example

```python
from zuora_sdk.models.invoice_settlement_async_job_response import InvoiceSettlementAsyncJobResponse

# TODO update the JSON string below
json = "{}"
# create an instance of InvoiceSettlementAsyncJobResponse from a JSON string
invoice_settlement_async_job_response_instance = InvoiceSettlementAsyncJobResponse.from_json(json)
# print the JSON string representation of the object
print(InvoiceSettlementAsyncJobResponse.to_json())

# convert the object into a dict
invoice_settlement_async_job_response_dict = invoice_settlement_async_job_response_instance.to_dict()
# create an instance of InvoiceSettlementAsyncJobResponse from a dict
invoice_settlement_async_job_response_from_dict = InvoiceSettlementAsyncJobResponse.from_dict(invoice_settlement_async_job_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


