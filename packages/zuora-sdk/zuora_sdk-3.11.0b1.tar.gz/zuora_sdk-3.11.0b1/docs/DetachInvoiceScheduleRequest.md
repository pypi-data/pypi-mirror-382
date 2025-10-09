# DetachInvoiceScheduleRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**specific_subscriptions** | [**List[InvoiceScheduleSubscription]**](InvoiceScheduleSubscription.md) | A list of the numbers of specific charge numbers to be detached from the invoice schedule  | [optional] 

## Example

```python
from zuora_sdk.models.detach_invoice_schedule_request import DetachInvoiceScheduleRequest

# TODO update the JSON string below
json = "{}"
# create an instance of DetachInvoiceScheduleRequest from a JSON string
detach_invoice_schedule_request_instance = DetachInvoiceScheduleRequest.from_json(json)
# print the JSON string representation of the object
print(DetachInvoiceScheduleRequest.to_json())

# convert the object into a dict
detach_invoice_schedule_request_dict = detach_invoice_schedule_request_instance.to_dict()
# create an instance of DetachInvoiceScheduleRequest from a dict
detach_invoice_schedule_request_from_dict = DetachInvoiceScheduleRequest.from_dict(detach_invoice_schedule_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


