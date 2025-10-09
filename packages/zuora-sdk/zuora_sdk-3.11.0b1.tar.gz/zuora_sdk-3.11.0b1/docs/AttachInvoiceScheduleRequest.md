# AttachInvoiceScheduleRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**specific_subscriptions** | [**List[InvoiceScheduleSubscription]**](InvoiceScheduleSubscription.md) | A list of the numbers of specific charge numbers to be attached to the invoice schedule  | [optional] 

## Example

```python
from zuora_sdk.models.attach_invoice_schedule_request import AttachInvoiceScheduleRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AttachInvoiceScheduleRequest from a JSON string
attach_invoice_schedule_request_instance = AttachInvoiceScheduleRequest.from_json(json)
# print the JSON string representation of the object
print(AttachInvoiceScheduleRequest.to_json())

# convert the object into a dict
attach_invoice_schedule_request_dict = attach_invoice_schedule_request_instance.to_dict()
# create an instance of AttachInvoiceScheduleRequest from a dict
attach_invoice_schedule_request_from_dict = AttachInvoiceScheduleRequest.from_dict(attach_invoice_schedule_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


