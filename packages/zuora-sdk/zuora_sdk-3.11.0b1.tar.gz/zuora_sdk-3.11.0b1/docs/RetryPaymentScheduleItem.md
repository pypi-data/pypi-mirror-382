# RetryPaymentScheduleItem

Information of the payment schedule items to be retried. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Specifies the ID of the payment schedule item to be retried.  | [optional] 
**payment_gateway_id** | **str** | Specifies the ID of a payment gateway that will be used in the retry.  | [optional] 
**payment_method_id** | **str** | Specifies the ID of a payment method that will be used in the retry.  | [optional] 

## Example

```python
from zuora_sdk.models.retry_payment_schedule_item import RetryPaymentScheduleItem

# TODO update the JSON string below
json = "{}"
# create an instance of RetryPaymentScheduleItem from a JSON string
retry_payment_schedule_item_instance = RetryPaymentScheduleItem.from_json(json)
# print the JSON string representation of the object
print(RetryPaymentScheduleItem.to_json())

# convert the object into a dict
retry_payment_schedule_item_dict = retry_payment_schedule_item_instance.to_dict()
# create an instance of RetryPaymentScheduleItem from a dict
retry_payment_schedule_item_from_dict = RetryPaymentScheduleItem.from_dict(retry_payment_schedule_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


