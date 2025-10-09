# UpdateInvoiceScheduleRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**additional_subscriptions_to_bill** | **List[str]** | A list of the numbers of the subscriptions that need to be billed together with the invoice schedule.   One invoice schedule can have at most 600 additional subscriptions.  | [optional] 
**invoice_separately** | **bool** | Whether the invoice items created from the invoice schedule appears on a separate invoice when Zuora generates invoices.  | [optional] 
**next_run_date** | **date** | The run date of the next execution of the invoice schedule.   By default, the next run date is the same as the run date of next pending invoice schedule item. The date can be overwritten by a different date other than the default value. If the invoice schedule has completed the execution, the next run date is &#x60;null&#x60;.  | [optional] 
**notes** | **str** | Comments on the invoice schedule.  | [optional] 
**orders** | **List[str]** | A list of the IDs or numbers of the orders associated with the invoice schedule. One invoice schedule can be associated with at most 10 orders.  The orders specified in this field override all the existing orders associated with the invoice schedule.  | [optional] 
**schedule_items** | [**List[UpdateInvoiceScheduleItem]**](UpdateInvoiceScheduleItem.md) | Container for invoice schedule items. The maximum number of schedule items is 50.  The invoice schedule items specified in this field override all the existing invoice schedule items.  | [optional] 
**specific_subscriptions** | [**List[InvoiceScheduleSubscription]**](InvoiceScheduleSubscription.md) | A list of the numbers of specific subscriptions associated with the invoice schedule.  - If the subscriptions specified in this field belong to the orders specified in the &#x60;orders&#x60; field, only the specific subscriptions instead of the orders are associated with the invoice schedule.  - If only the &#x60;orders&#x60; field is specified, all the subscriptions from the order are associated with the invoice schedule.    The specific subscriptions specified in this field override all the existing specific subscriptions associated with the invoice schedule.  Example: &#x60;&#x60;&#x60; {   \&quot;orders\&quot;: [     \&quot;O-00000001\&quot;, \&quot;O-00000002\&quot;   ],   \&quot;specificSubscriptions\&quot;: [     {       \&quot;orderKey\&quot;: \&quot;O-00000001\&quot;,       \&quot;subscriptionKey\&quot;: \&quot;S-00000001\&quot;     }   ] } &#x60;&#x60;&#x60; - For the order with number O-00000001, only subscription S-00000001 contained in the order is associated with the invoice schedule. - For the order with number O-00000002, all subscriptions contained in the order are associated with the invoice schedule.  | [optional] 

## Example

```python
from zuora_sdk.models.update_invoice_schedule_request import UpdateInvoiceScheduleRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateInvoiceScheduleRequest from a JSON string
update_invoice_schedule_request_instance = UpdateInvoiceScheduleRequest.from_json(json)
# print the JSON string representation of the object
print(UpdateInvoiceScheduleRequest.to_json())

# convert the object into a dict
update_invoice_schedule_request_dict = update_invoice_schedule_request_instance.to_dict()
# create an instance of UpdateInvoiceScheduleRequest from a dict
update_invoice_schedule_request_from_dict = UpdateInvoiceScheduleRequest.from_dict(update_invoice_schedule_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


