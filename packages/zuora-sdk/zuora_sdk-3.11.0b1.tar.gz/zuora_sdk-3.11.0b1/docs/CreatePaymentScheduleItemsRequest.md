# CreatePaymentScheduleItemsRequest

Container for the payment schedule items to be added to the payment schedule. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**List[CreatePaymentScheduleItemsRequestItems]**](CreatePaymentScheduleItemsRequestItems.md) |  | 

## Example

```python
from zuora_sdk.models.create_payment_schedule_items_request import CreatePaymentScheduleItemsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreatePaymentScheduleItemsRequest from a JSON string
create_payment_schedule_items_request_instance = CreatePaymentScheduleItemsRequest.from_json(json)
# print the JSON string representation of the object
print(CreatePaymentScheduleItemsRequest.to_json())

# convert the object into a dict
create_payment_schedule_items_request_dict = create_payment_schedule_items_request_instance.to_dict()
# create an instance of CreatePaymentScheduleItemsRequest from a dict
create_payment_schedule_items_request_from_dict = CreatePaymentScheduleItemsRequest.from_dict(create_payment_schedule_items_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


