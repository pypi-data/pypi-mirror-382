# RetryPaymentScheduleItemRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**List[RetryPaymentScheduleItem]**](RetryPaymentScheduleItem.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.retry_payment_schedule_item_request import RetryPaymentScheduleItemRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RetryPaymentScheduleItemRequest from a JSON string
retry_payment_schedule_item_request_instance = RetryPaymentScheduleItemRequest.from_json(json)
# print the JSON string representation of the object
print(RetryPaymentScheduleItemRequest.to_json())

# convert the object into a dict
retry_payment_schedule_item_request_dict = retry_payment_schedule_item_request_instance.to_dict()
# create an instance of RetryPaymentScheduleItemRequest from a dict
retry_payment_schedule_item_request_from_dict = RetryPaymentScheduleItemRequest.from_dict(retry_payment_schedule_item_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


