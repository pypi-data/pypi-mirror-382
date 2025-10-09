# UpdateInvoiceScheduleItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **decimal.Decimal** | The amount of the invoice to be generated during the processing of the invoice schedule item. You can only specify one of the &#x60;amount&#x60; and &#x60;percentage&#x60; fields.  | [optional] 
**id** | **str** | The unique ID of the invoice schedule item to be updated.   If this field is not provided, a new invoice schedule item is added to the invoice schedule.  | [optional] 
**name** | **str** | The name of the invoice schedule item.  | [optional] 
**percentage** | **decimal.Decimal** | The percentage of the total amount to be generated during the processing of the invoice schedule item. The field value must be greater than 0. You can only specify one of the &#x60;amount&#x60; and &#x60;percentage&#x60; fields. | [optional] 
**run_date** | **date** | The date in the tenant’s time zone when the invoice schedule item is planned to be processed to generate an invoice.  | [optional] 
**target_date_for_additional_subscriptions** | **date** | The date in the tenant&#39;s time zone used by the invoice schedule to determine which fixed-period regular charges to be billed together with the invoice schedule item.   The regular charges must come from the subscriptions specified in the &#x60;additionalSubscriptionsToBill&#x60; field.  | [optional] 

## Example

```python
from zuora_sdk.models.update_invoice_schedule_item import UpdateInvoiceScheduleItem

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateInvoiceScheduleItem from a JSON string
update_invoice_schedule_item_instance = UpdateInvoiceScheduleItem.from_json(json)
# print the JSON string representation of the object
print(UpdateInvoiceScheduleItem.to_json())

# convert the object into a dict
update_invoice_schedule_item_dict = update_invoice_schedule_item_instance.to_dict()
# create an instance of UpdateInvoiceScheduleItem from a dict
update_invoice_schedule_item_from_dict = UpdateInvoiceScheduleItem.from_dict(update_invoice_schedule_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


