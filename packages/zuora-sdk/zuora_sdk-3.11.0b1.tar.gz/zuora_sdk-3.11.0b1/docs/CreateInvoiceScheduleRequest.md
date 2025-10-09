# CreateInvoiceScheduleRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**account_key** | **str** | The ID or number of the account associated with the invoice schedule.  | 
**additional_subscriptions_to_bill** | **List[str]** | A list of the numbers of the subscriptions that need to be billed together with the invoice schedule.   One invoice schedule can have at most 600 additional subscriptions.  | [optional] 
**invoice_separately** | **bool** | Whether the invoice items created from the invoice schedule appears on a separate invoice when Zuora generates invoices.  | [optional] 
**notes** | **str** | Comments on the invoice schedule.  | [optional] 
**orders** | **List[str]** | A list of the IDs or numbers of the orders associated with the invoice schedule. One invoice schedule can be associated with at most 10 orders.  | 
**schedule_items** | [**List[CreateInvoiceScheduleItem]**](CreateInvoiceScheduleItem.md) | Container for invoice schedule items. One invoice schedule can have at most 50 invoice schedule items.  | [optional] 
**specific_subscriptions** | [**List[InvoiceScheduleSubscription]**](InvoiceScheduleSubscription.md) | A list of the numbers of specific subscriptions associated with the invoice schedule.  - If the subscriptions specified in this field belong to the orders specified in the &#x60;orders&#x60; field, only the specific subscriptions instead of the orders are associated with the invoice schedule.  - If only the &#x60;orders&#x60; field is specified, all the subscriptions from the order are associated with the invoice schedule.  Example: &#x60;&#x60;&#x60; {   \&quot;orders\&quot;: [     \&quot;O-00000001\&quot;, \&quot;O-00000002\&quot;   ],   \&quot;specificSubscriptions\&quot;: [     {       \&quot;orderKey\&quot;: \&quot;O-00000001\&quot;,       \&quot;subscriptionKey\&quot;: \&quot;S-00000001\&quot;     }   ] } &#x60;&#x60;&#x60; - For the order with number O-00000001, only subscription S-00000001 contained in the order is associated with the invoice schedule. - For the order with number O-00000002, all subscriptions contained in the order are associated with the invoice schedule.  | [optional] 

## Example

```python
from zuora_sdk.models.create_invoice_schedule_request import CreateInvoiceScheduleRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateInvoiceScheduleRequest from a JSON string
create_invoice_schedule_request_instance = CreateInvoiceScheduleRequest.from_json(json)
# print the JSON string representation of the object
print(CreateInvoiceScheduleRequest.to_json())

# convert the object into a dict
create_invoice_schedule_request_dict = create_invoice_schedule_request_instance.to_dict()
# create an instance of CreateInvoiceScheduleRequest from a dict
create_invoice_schedule_request_from_dict = CreateInvoiceScheduleRequest.from_dict(create_invoice_schedule_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


