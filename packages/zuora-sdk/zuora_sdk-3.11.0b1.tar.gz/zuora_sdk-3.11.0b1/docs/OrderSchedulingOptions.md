# OrderSchedulingOptions

Information of scheduled order.  **Note**: The Scheduled Orders feature is in the Early Adopter phase. We are actively soliciting feedback from a small set of early adopters before releasing it as generally available. If you want to join this early adopter program, submit a request at <a href=\"https://support.zuora.com/hc/en-us\" target=\"_blank\">Zuora Global Support</a>. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**scheduled_date** | **date** | The date for the order scheduled.  | [optional] 
**scheduled_date_policy** | [**OrderScheduledDatePolicy**](OrderScheduledDatePolicy.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.order_scheduling_options import OrderSchedulingOptions

# TODO update the JSON string below
json = "{}"
# create an instance of OrderSchedulingOptions from a JSON string
order_scheduling_options_instance = OrderSchedulingOptions.from_json(json)
# print the JSON string representation of the object
print(OrderSchedulingOptions.to_json())

# convert the object into a dict
order_scheduling_options_dict = order_scheduling_options_instance.to_dict()
# create an instance of OrderSchedulingOptions from a dict
order_scheduling_options_from_dict = OrderSchedulingOptions.from_dict(order_scheduling_options_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


