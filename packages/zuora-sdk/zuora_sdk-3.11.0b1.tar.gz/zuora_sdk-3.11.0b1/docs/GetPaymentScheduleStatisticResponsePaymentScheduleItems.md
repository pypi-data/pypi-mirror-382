# GetPaymentScheduleStatisticResponsePaymentScheduleItems


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**error** | **int** | The number of errored payment schedule items.                | [optional] 
**pending** | **int** | The number of pending payment schedule items.  | [optional] 
**processed** | **int** | The number of processed payment schedule items.   | [optional] 

## Example

```python
from zuora_sdk.models.get_payment_schedule_statistic_response_payment_schedule_items import GetPaymentScheduleStatisticResponsePaymentScheduleItems

# TODO update the JSON string below
json = "{}"
# create an instance of GetPaymentScheduleStatisticResponsePaymentScheduleItems from a JSON string
get_payment_schedule_statistic_response_payment_schedule_items_instance = GetPaymentScheduleStatisticResponsePaymentScheduleItems.from_json(json)
# print the JSON string representation of the object
print(GetPaymentScheduleStatisticResponsePaymentScheduleItems.to_json())

# convert the object into a dict
get_payment_schedule_statistic_response_payment_schedule_items_dict = get_payment_schedule_statistic_response_payment_schedule_items_instance.to_dict()
# create an instance of GetPaymentScheduleStatisticResponsePaymentScheduleItems from a dict
get_payment_schedule_statistic_response_payment_schedule_items_from_dict = GetPaymentScheduleStatisticResponsePaymentScheduleItems.from_dict(get_payment_schedule_statistic_response_payment_schedule_items_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


