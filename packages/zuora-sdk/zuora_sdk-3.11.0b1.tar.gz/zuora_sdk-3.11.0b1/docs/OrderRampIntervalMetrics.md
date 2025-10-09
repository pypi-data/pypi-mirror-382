# OrderRampIntervalMetrics


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** | The short description of the interval. | [optional] 
**discount_tcb** | **float** | The discount amount for the TCB. | [optional] 
**discount_tcv** | **float** | The discount amount for the TCV. | [optional] 
**end_date** | **date** | The end date of the interval. | [optional] 
**gross_tcb** | **float** | The gross TCB value before discount charges are applied. | [optional] 
**gross_tcv** | **float** | The gross TCV value before discount charges are applied. | [optional] 
**interval_delta_metrics** | [**List[RampIntervalChargeDeltaMetrics]**](RampIntervalChargeDeltaMetrics.md) | Container for the delta metrics for each rate plan charge in each ramp interval. The delta is the difference of the subscription metrics between before and after the order. | [optional] 
**interval_metrics** | [**List[RampIntervalChargeMetrics]**](RampIntervalChargeMetrics.md) | Container for the detailed metrics for each rate plan charge in each ramp interval. | [optional] 
**name** | **str** | The name of the interval. | [optional] 
**net_tcb** | **float** | The net TCB value after discount charges are applied. | [optional] 
**net_tcv** | **float** | The net TCV value after discount charges are applied. | [optional] 
**start_date** | **date** | The start date of the interval. | [optional] 

## Example

```python
from zuora_sdk.models.order_ramp_interval_metrics import OrderRampIntervalMetrics

# TODO update the JSON string below
json = "{}"
# create an instance of OrderRampIntervalMetrics from a JSON string
order_ramp_interval_metrics_instance = OrderRampIntervalMetrics.from_json(json)
# print the JSON string representation of the object
print(OrderRampIntervalMetrics.to_json())

# convert the object into a dict
order_ramp_interval_metrics_dict = order_ramp_interval_metrics_instance.to_dict()
# create an instance of OrderRampIntervalMetrics from a dict
order_ramp_interval_metrics_from_dict = OrderRampIntervalMetrics.from_dict(order_ramp_interval_metrics_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


