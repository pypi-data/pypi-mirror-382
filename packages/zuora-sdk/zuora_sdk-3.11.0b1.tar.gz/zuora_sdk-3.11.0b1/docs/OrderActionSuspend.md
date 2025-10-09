# OrderActionSuspend

Information about an order action of type `Suspend`. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**suspend_date** | **date** | The suspend date when the suspension takes effect.   | [optional] 
**suspend_periods** | **int** | This field is applicable only when the &#x60;suspendPolicy&#x60; field is set to &#x60;FixedPeriodsFromToday&#x60;. It must be used together with the &#x60;suspendPeriodsType&#x60; field. Note this field is not applicable in a Suspend order action auto-created by the Order Metrics migration.  The total number of the periods used to specify when a subscription suspension takes effect. The subscription suspension will take place after the specified time frame (&#x60;suspendPeriods&#x60; multiplied by &#x60;suspendPeriodsType&#x60;) from today&#39;s date.   | [optional] 
**suspend_periods_type** | [**SuspendPeriodsType**](SuspendPeriodsType.md) |  | [optional] 
**suspend_policy** | [**SuspendPolicy**](SuspendPolicy.md) |  | [optional] 
**suspend_specific_date** | **date** | This field is applicable only when the &#x60;suspendPolicy&#x60; field is set to &#x60;SpecificDate&#x60;. Note this field is not applicable in a Suspend order action auto-created by the Order Metrics migration.  A specific date when the subscription suspension takes effect, in YYYY-MM-DD format. The value should not be earlier than the subscription&#39;s contract effective date or later than the subscription&#39;s term end date.  | [optional] 

## Example

```python
from zuora_sdk.models.order_action_suspend import OrderActionSuspend

# TODO update the JSON string below
json = "{}"
# create an instance of OrderActionSuspend from a JSON string
order_action_suspend_instance = OrderActionSuspend.from_json(json)
# print the JSON string representation of the object
print(OrderActionSuspend.to_json())

# convert the object into a dict
order_action_suspend_dict = order_action_suspend_instance.to_dict()
# create an instance of OrderActionSuspend from a dict
order_action_suspend_from_dict = OrderActionSuspend.from_dict(order_action_suspend_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


