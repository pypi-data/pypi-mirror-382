# InvoiceScheduleSubscription


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**order_key** | **str** | The unique ID or number of the order associated with the invoice schedule.  | [optional] 
**subscription_key** | **str** | The unique number of the subscription contained in the order associated with the invoice schedule. | [optional] 
**charge_numbers** | **List[str]** | A list of the numbers of charges contained in the subscription\&quot; | [optional] 

## Example

```python
from zuora_sdk.models.invoice_schedule_subscription import InvoiceScheduleSubscription

# TODO update the JSON string below
json = "{}"
# create an instance of InvoiceScheduleSubscription from a JSON string
invoice_schedule_subscription_instance = InvoiceScheduleSubscription.from_json(json)
# print the JSON string representation of the object
print(InvoiceScheduleSubscription.to_json())

# convert the object into a dict
invoice_schedule_subscription_dict = invoice_schedule_subscription_instance.to_dict()
# create an instance of InvoiceScheduleSubscription from a dict
invoice_schedule_subscription_from_dict = InvoiceScheduleSubscription.from_dict(invoice_schedule_subscription_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


