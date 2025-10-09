# CreateOrderSuspend

Information about an order action of type `Suspend`. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**suspend_periods** | **int** | This field is applicable only when the &#x60;suspendPolicy&#x60; field is set to &#x60;FixedPeriodsFromToday&#x60;. It must be used together with the &#x60;suspendPeriodsType&#x60; field.   The total number of the periods used to specify when a subscription suspension takes effect. The subscription suspension will take place after the specified time frame (&#x60;suspendPeriods&#x60; multiplied by &#x60;suspendPeriodsType&#x60;) from today&#39;s date.   | [optional] 
**suspend_periods_type** | [**SuspendPeriodsType**](SuspendPeriodsType.md) |  | [optional] 
**suspend_policy** | [**SuspendPolicy**](SuspendPolicy.md) |  | 
**suspend_specific_date** | **date** | This field is applicable only when the &#x60;suspendPolicy&#x60; field is set to &#x60;SpecificDate&#x60;.  A specific date when the subscription suspension takes effect, in YYYY-MM-DD format. The value should not be earlier than the subscription&#39;s contract effective date or later than the subscription&#39;s term end date.  | [optional] 

## Example

```python
from zuora_sdk.models.create_order_suspend import CreateOrderSuspend

# TODO update the JSON string below
json = "{}"
# create an instance of CreateOrderSuspend from a JSON string
create_order_suspend_instance = CreateOrderSuspend.from_json(json)
# print the JSON string representation of the object
print(CreateOrderSuspend.to_json())

# convert the object into a dict
create_order_suspend_dict = create_order_suspend_instance.to_dict()
# create an instance of CreateOrderSuspend from a dict
create_order_suspend_from_dict = CreateOrderSuspend.from_dict(create_order_suspend_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


