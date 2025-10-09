# ExecuteInvoiceScheduleRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**schedule_item_id** | **str** | The ID of the invoice schedule item to be executed.   The item must be the earliest pending schedule item. If all the invoice schedule items have been processed and credit is needed to be generated, do not specify this field in the request. | [optional] 

## Example

```python
from zuora_sdk.models.execute_invoice_schedule_request import ExecuteInvoiceScheduleRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ExecuteInvoiceScheduleRequest from a JSON string
execute_invoice_schedule_request_instance = ExecuteInvoiceScheduleRequest.from_json(json)
# print the JSON string representation of the object
print(ExecuteInvoiceScheduleRequest.to_json())

# convert the object into a dict
execute_invoice_schedule_request_dict = execute_invoice_schedule_request_instance.to_dict()
# create an instance of ExecuteInvoiceScheduleRequest from a dict
execute_invoice_schedule_request_from_dict = ExecuteInvoiceScheduleRequest.from_dict(execute_invoice_schedule_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


