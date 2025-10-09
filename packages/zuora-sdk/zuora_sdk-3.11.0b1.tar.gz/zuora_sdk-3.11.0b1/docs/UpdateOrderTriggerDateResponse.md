# UpdateOrderTriggerDateResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**UpdateOrderTriggerDatesSubscriptionsStatus**](UpdateOrderTriggerDatesSubscriptionsStatus.md) |  | [optional] 
**subscription_number** | **str** | Subscription number of the subscription updated. | [optional] 

## Example

```python
from zuora_sdk.models.update_order_trigger_date_response import UpdateOrderTriggerDateResponse

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateOrderTriggerDateResponse from a JSON string
update_order_trigger_date_response_instance = UpdateOrderTriggerDateResponse.from_json(json)
# print the JSON string representation of the object
print(UpdateOrderTriggerDateResponse.to_json())

# convert the object into a dict
update_order_trigger_date_response_dict = update_order_trigger_date_response_instance.to_dict()
# create an instance of UpdateOrderTriggerDateResponse from a dict
update_order_trigger_date_response_from_dict = UpdateOrderTriggerDateResponse.from_dict(update_order_trigger_date_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


