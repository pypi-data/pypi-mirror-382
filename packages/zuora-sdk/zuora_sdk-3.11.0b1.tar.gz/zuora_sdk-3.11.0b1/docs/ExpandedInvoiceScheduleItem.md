# ExpandedInvoiceScheduleItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**amount** | **float** |  | [optional] 
**actual_amount** | **float** |  | [optional] 
**run_date** | **date** |  | [optional] 
**invoice_schedule_id** | **str** |  | [optional] 
**invoice_id** | **str** |  | [optional] 
**credit_memo_id** | **str** |  | [optional] 
**status** | **str** |  | [optional] 
**name** | **str** |  | [optional] 
**sequence_number** | **int** |  | [optional] 
**target_date_for_additional_subscriptions** | **date** |  | [optional] 
**percentage** | **float** |  | [optional] 
**invoice** | [**ExpandedInvoice**](ExpandedInvoice.md) |  | [optional] 
**credit_memo** | [**ExpandedCreditMemo**](ExpandedCreditMemo.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_invoice_schedule_item import ExpandedInvoiceScheduleItem

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedInvoiceScheduleItem from a JSON string
expanded_invoice_schedule_item_instance = ExpandedInvoiceScheduleItem.from_json(json)
# print the JSON string representation of the object
print(ExpandedInvoiceScheduleItem.to_json())

# convert the object into a dict
expanded_invoice_schedule_item_dict = expanded_invoice_schedule_item_instance.to_dict()
# create an instance of ExpandedInvoiceScheduleItem from a dict
expanded_invoice_schedule_item_from_dict = ExpandedInvoiceScheduleItem.from_dict(expanded_invoice_schedule_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


