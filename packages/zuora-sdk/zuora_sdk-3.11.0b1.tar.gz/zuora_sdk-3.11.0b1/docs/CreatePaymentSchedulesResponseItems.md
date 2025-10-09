# CreatePaymentSchedulesResponseItems


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The ID of the created payment schedule.  | [optional] 
**payment_schedule_number** | **str** | The number of the created payment schedule.  | [optional] 

## Example

```python
from zuora_sdk.models.create_payment_schedules_response_items import CreatePaymentSchedulesResponseItems

# TODO update the JSON string below
json = "{}"
# create an instance of CreatePaymentSchedulesResponseItems from a JSON string
create_payment_schedules_response_items_instance = CreatePaymentSchedulesResponseItems.from_json(json)
# print the JSON string representation of the object
print(CreatePaymentSchedulesResponseItems.to_json())

# convert the object into a dict
create_payment_schedules_response_items_dict = create_payment_schedules_response_items_instance.to_dict()
# create an instance of CreatePaymentSchedulesResponseItems from a dict
create_payment_schedules_response_items_from_dict = CreatePaymentSchedulesResponseItems.from_dict(create_payment_schedules_response_items_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


