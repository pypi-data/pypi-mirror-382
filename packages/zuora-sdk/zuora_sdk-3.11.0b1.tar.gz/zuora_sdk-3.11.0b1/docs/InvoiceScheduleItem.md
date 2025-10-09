# InvoiceScheduleItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**actual_amount** | **decimal.Decimal** | The actual amount that needs to be billed during the processing of the invoice schedule item.  By default, the actual amount is the same as the total amount. Even if order changes occur like Remove Product or Cancel Subscription, the value of the &#x60;amount&#x60; field keeps unchanged. The value of the &#x60;actualAmount&#x60; field reflects the actual amount to be billed.  | [optional] 
**amount** | **decimal.Decimal** | The amount of the invoice generated during the processing of the invoice schedule item.  The value of this field keeps unchanged once invoice schedule items are created.  | [optional] 
**credit_memo_id** | **str** | The ID of the credit memo that is generated during the processing of the invoice schedule item.  | [optional] 
**id** | **str** | The unique ID of the invoice schedule item.  | [optional] 
**invoice_id** | **str** | The ID of the invoice that is generated during the processing of the invoice schedule item.  | [optional] 
**name** | **str** | The name of the invoice schedule item.  | [optional] 
**percentage** | **decimal.Decimal** | The percentage of the total amount to be generated during the processing of the invoice schedule item. | [optional] 
**run_date** | **date** | The date in the tenant’s time zone when the invoice schedule item is processed to generate an invoice.  | [optional] 
**status** | [**InvoiceScheduleItemStatus**](InvoiceScheduleItemStatus.md) |  | [optional] 
**target_date_for_additional_subscriptions** | **date** | The date in the tenant&#39;s time zone used by the invoice schedule to determine which fixed-period regular charges to be billed together with the invoice schedule item.   The regular charges must come from the subscriptions specified in the &#x60;additionalSubscriptionsToBill&#x60; field.  | [optional] 

## Example

```python
from zuora_sdk.models.invoice_schedule_item import InvoiceScheduleItem

# TODO update the JSON string below
json = "{}"
# create an instance of InvoiceScheduleItem from a JSON string
invoice_schedule_item_instance = InvoiceScheduleItem.from_json(json)
# print the JSON string representation of the object
print(InvoiceScheduleItem.to_json())

# convert the object into a dict
invoice_schedule_item_dict = invoice_schedule_item_instance.to_dict()
# create an instance of InvoiceScheduleItem from a dict
invoice_schedule_item_from_dict = InvoiceScheduleItem.from_dict(invoice_schedule_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


