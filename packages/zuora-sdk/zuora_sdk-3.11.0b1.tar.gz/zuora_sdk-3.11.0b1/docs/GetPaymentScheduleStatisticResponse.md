# GetPaymentScheduleStatisticResponse

The object that contains the payment schedule statistic of the specified date. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_date** | **date** | The specified date.  | [optional] 
**payment_runs** | [**List[GetPaymentRunStatisticResponse]**](GetPaymentRunStatisticResponse.md) |  | [optional] 
**payment_schedule_items** | [**GetPaymentScheduleStatisticResponsePaymentScheduleItems**](GetPaymentScheduleStatisticResponsePaymentScheduleItems.md) |  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.  | [optional] 

## Example

```python
from zuora_sdk.models.get_payment_schedule_statistic_response import GetPaymentScheduleStatisticResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetPaymentScheduleStatisticResponse from a JSON string
get_payment_schedule_statistic_response_instance = GetPaymentScheduleStatisticResponse.from_json(json)
# print the JSON string representation of the object
print(GetPaymentScheduleStatisticResponse.to_json())

# convert the object into a dict
get_payment_schedule_statistic_response_dict = get_payment_schedule_statistic_response_instance.to_dict()
# create an instance of GetPaymentScheduleStatisticResponse from a dict
get_payment_schedule_statistic_response_from_dict = GetPaymentScheduleStatisticResponse.from_dict(get_payment_schedule_statistic_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


