# GetPaymentRunStatisticResponse

Payment run statistic.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**completed_on** | **datetime** | The date and time the payment run is completed.  | [optional] 
**executed_on** | **datetime** | The date and time the payment run is executed.  | [optional] 
**number** | **str** | Payment run number.  | [optional] 
**number_of_errors** | **int** | Number of errored payments  | [optional] 
**number_of_payments** | **int** | Number of processed payments.  | [optional] 
**status** | **str** | Payment run status.  | [optional] 

## Example

```python
from zuora_sdk.models.get_payment_run_statistic_response import GetPaymentRunStatisticResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetPaymentRunStatisticResponse from a JSON string
get_payment_run_statistic_response_instance = GetPaymentRunStatisticResponse.from_json(json)
# print the JSON string representation of the object
print(GetPaymentRunStatisticResponse.to_json())

# convert the object into a dict
get_payment_run_statistic_response_dict = get_payment_run_statistic_response_instance.to_dict()
# create an instance of GetPaymentRunStatisticResponse from a dict
get_payment_run_statistic_response_from_dict = GetPaymentRunStatisticResponse.from_dict(get_payment_run_statistic_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


