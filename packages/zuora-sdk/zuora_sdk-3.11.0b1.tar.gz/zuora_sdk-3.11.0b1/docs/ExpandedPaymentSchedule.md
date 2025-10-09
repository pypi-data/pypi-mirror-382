# ExpandedPaymentSchedule


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**number** | **str** |  | [optional] 
**account_id** | **str** |  | [optional] 
**invoice_id** | **str** |  | [optional] 
**debitmemo_id** | **str** |  | [optional] 
**payment_option_id** | **str** |  | [optional] 
**start_date** | **date** |  | [optional] 
**run_hour** | **int** |  | [optional] 
**period** | **str** |  | [optional] 
**prepayment** | **bool** |  | [optional] 
**occurrences** | **int** |  | [optional] 
**status** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**next_payment_date** | **date** |  | [optional] 
**recent_payment_date** | **date** |  | [optional] 
**total_payments_processed** | **int** |  | [optional] 
**total_payments_errored** | **int** |  | [optional] 
**total_amount** | **float** |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_payment_schedule import ExpandedPaymentSchedule

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedPaymentSchedule from a JSON string
expanded_payment_schedule_instance = ExpandedPaymentSchedule.from_json(json)
# print the JSON string representation of the object
print(ExpandedPaymentSchedule.to_json())

# convert the object into a dict
expanded_payment_schedule_dict = expanded_payment_schedule_instance.to_dict()
# create an instance of ExpandedPaymentSchedule from a dict
expanded_payment_schedule_from_dict = ExpandedPaymentSchedule.from_dict(expanded_payment_schedule_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


