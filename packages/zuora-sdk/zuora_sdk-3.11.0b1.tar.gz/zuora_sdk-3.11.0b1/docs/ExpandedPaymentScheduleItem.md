# ExpandedPaymentScheduleItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**number** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**account_id** | **str** |  | [optional] 
**invoice_id** | **str** |  | [optional] 
**debitmemo_id** | **str** |  | [optional] 
**payment_schedule_id** | **str** |  | [optional] 
**payment_option_id** | **str** |  | [optional] 
**prepayment** | **bool** |  | [optional] 
**scheduled_date** | **date** |  | [optional] 
**run_hour** | **int** |  | [optional] 
**payment_method_id** | **str** |  | [optional] 
**payment_gateway_id** | **str** |  | [optional] 
**amount** | **float** |  | [optional] 
**balance** | **float** |  | [optional] 
**currency** | **str** |  | [optional] 
**status** | **str** |  | [optional] 
**error_message** | **str** |  | [optional] 
**payment_id** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**cancellation_reason** | **str** |  | [optional] 
**payment_schedule_item_payments** | [**List[ExpandedPaymentScheduleItemPayment]**](ExpandedPaymentScheduleItemPayment.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_payment_schedule_item import ExpandedPaymentScheduleItem

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedPaymentScheduleItem from a JSON string
expanded_payment_schedule_item_instance = ExpandedPaymentScheduleItem.from_json(json)
# print the JSON string representation of the object
print(ExpandedPaymentScheduleItem.to_json())

# convert the object into a dict
expanded_payment_schedule_item_dict = expanded_payment_schedule_item_instance.to_dict()
# create an instance of ExpandedPaymentScheduleItem from a dict
expanded_payment_schedule_item_from_dict = ExpandedPaymentScheduleItem.from_dict(expanded_payment_schedule_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


