# CancelPaymentSchedule


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**cancel_date** | **date** | Specifies when the payment schedule will be canceled.  | 

## Example

```python
from zuora_sdk.models.cancel_payment_schedule import CancelPaymentSchedule

# TODO update the JSON string below
json = "{}"
# create an instance of CancelPaymentSchedule from a JSON string
cancel_payment_schedule_instance = CancelPaymentSchedule.from_json(json)
# print the JSON string representation of the object
print(CancelPaymentSchedule.to_json())

# convert the object into a dict
cancel_payment_schedule_dict = cancel_payment_schedule_instance.to_dict()
# create an instance of CancelPaymentSchedule from a dict
cancel_payment_schedule_from_dict = CancelPaymentSchedule.from_dict(cancel_payment_schedule_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


