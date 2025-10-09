# ExpandedPaymentScheduleItemPayment


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**payment_schedule_item_id** | **str** |  | [optional] 
**payment_id** | **str** |  | [optional] 
**payment** | [**ExpandedPayment**](ExpandedPayment.md) |  | [optional] 
**payment_schedule_item** | [**ExpandedPaymentScheduleItem**](ExpandedPaymentScheduleItem.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_payment_schedule_item_payment import ExpandedPaymentScheduleItemPayment

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedPaymentScheduleItemPayment from a JSON string
expanded_payment_schedule_item_payment_instance = ExpandedPaymentScheduleItemPayment.from_json(json)
# print the JSON string representation of the object
print(ExpandedPaymentScheduleItemPayment.to_json())

# convert the object into a dict
expanded_payment_schedule_item_payment_dict = expanded_payment_schedule_item_payment_instance.to_dict()
# create an instance of ExpandedPaymentScheduleItemPayment from a dict
expanded_payment_schedule_item_payment_from_dict = ExpandedPaymentScheduleItemPayment.from_dict(expanded_payment_schedule_item_payment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


