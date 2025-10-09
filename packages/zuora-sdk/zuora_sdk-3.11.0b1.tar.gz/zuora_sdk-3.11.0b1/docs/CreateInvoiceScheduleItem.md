# CreateInvoiceScheduleItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **decimal.Decimal** | The amount of the invoice to be generated during the processing of the invoice schedule item. You can only specify one of the &#x60;amount&#x60; and &#x60;percentage&#x60; fields.  | [optional] 
**name** | **str** | The name of the invoice schedule item.  | [optional] 
**percentage** | **decimal.Decimal** | The percentage of the total amount to be generated during the processing of the invoice schedule item. The field value must be greater than 0. You can only specify one of the &#x60;amount&#x60; and &#x60;percentage&#x60; fields. | [optional] 
**run_date** | **date** | The date in the tenant’s time zone when the invoice schedule item is planned to be processed to generate an invoice.   When specifying run dates for invoice schedule items, consider that: - An invoice schedule item with a blank run date will not be executed. - You can only update the run date for an invoice schedule item in Pending status. - If the run date of an invoice schedule item is left empty, the dates of all subsequent invoice schedule items must also be blank. - You must specify run dates in chronological order for invoice schedule items.                    | [optional] 
**target_date_for_additional_subscriptions** | **date** | The date in the tenant&#39;s time zone used by the invoice schedule to determine which fixed-period regular charges to be billed together with the invoice schedule item.   The regular charges must come from the subscriptions specified in the &#x60;additionalSubscriptionsToBill&#x60; field.  | [optional] 

## Example

```python
from zuora_sdk.models.create_invoice_schedule_item import CreateInvoiceScheduleItem

# TODO update the JSON string below
json = "{}"
# create an instance of CreateInvoiceScheduleItem from a JSON string
create_invoice_schedule_item_instance = CreateInvoiceScheduleItem.from_json(json)
# print the JSON string representation of the object
print(CreateInvoiceScheduleItem.to_json())

# convert the object into a dict
create_invoice_schedule_item_dict = create_invoice_schedule_item_instance.to_dict()
# create an instance of CreateInvoiceScheduleItem from a dict
create_invoice_schedule_item_from_dict = CreateInvoiceScheduleItem.from_dict(create_invoice_schedule_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


