# CreatePaymentSchedulesRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**payment_schedules** | [**List[CreatePaymentScheduleRequest]**](CreatePaymentScheduleRequest.md) | Container of the payment schedules to be created.  | 

## Example

```python
from zuora_sdk.models.create_payment_schedules_request import CreatePaymentSchedulesRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreatePaymentSchedulesRequest from a JSON string
create_payment_schedules_request_instance = CreatePaymentSchedulesRequest.from_json(json)
# print the JSON string representation of the object
print(CreatePaymentSchedulesRequest.to_json())

# convert the object into a dict
create_payment_schedules_request_dict = create_payment_schedules_request_instance.to_dict()
# create an instance of CreatePaymentSchedulesRequest from a dict
create_payment_schedules_request_from_dict = CreatePaymentSchedulesRequest.from_dict(create_payment_schedules_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


