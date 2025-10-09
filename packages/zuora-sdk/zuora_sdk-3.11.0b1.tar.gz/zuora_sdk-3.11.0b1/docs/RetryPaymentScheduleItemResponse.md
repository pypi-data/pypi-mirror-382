# RetryPaymentScheduleItemResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**List[PaymentScheduleItem]**](PaymentScheduleItem.md) |  | [optional] 
**success** | **bool** | Returns &#x60;true&#x60; if the request was processed successfully.   | [optional] 

## Example

```python
from zuora_sdk.models.retry_payment_schedule_item_response import RetryPaymentScheduleItemResponse

# TODO update the JSON string below
json = "{}"
# create an instance of RetryPaymentScheduleItemResponse from a JSON string
retry_payment_schedule_item_response_instance = RetryPaymentScheduleItemResponse.from_json(json)
# print the JSON string representation of the object
print(RetryPaymentScheduleItemResponse.to_json())

# convert the object into a dict
retry_payment_schedule_item_response_dict = retry_payment_schedule_item_response_instance.to_dict()
# create an instance of RetryPaymentScheduleItemResponse from a dict
retry_payment_schedule_item_response_from_dict = RetryPaymentScheduleItemResponse.from_dict(retry_payment_schedule_item_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


