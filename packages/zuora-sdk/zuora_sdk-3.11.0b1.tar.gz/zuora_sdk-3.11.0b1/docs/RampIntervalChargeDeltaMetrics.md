# RampIntervalChargeDeltaMetrics


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**charge_number** | **str** | The number of the rate plan charge. | [optional] 
**delta_discount_tcb** | **float** | The discount delta amount for the TCB. | [optional] 
**delta_discount_tcv** | **float** | The discount delta amount for the TCV. | [optional] 
**delta_gross_tcb** | **float** | The TCB delta value before discount charges are applied. | [optional] 
**delta_gross_tcv** | **float** | The TCV delta value before discount charges are applied. | [optional] 
**delta_mrr** | [**List[RampIntervalChargeDeltaMetricsDeltaMrrInner]**](RampIntervalChargeDeltaMetricsDeltaMrrInner.md) | The MRR changing history of the current rate plan charge in the current ramp interval. | [optional] 
**delta_net_tcb** | **float** | The TCB delta value after discount charges are applied. | [optional] 
**delta_net_tcv** | **float** | The TCV delta value after discount charges are applied. | [optional] 
**delta_quantity** | [**List[RampIntervalChargeDeltaMetricsDeltaQuantityInner]**](RampIntervalChargeDeltaMetricsDeltaQuantityInner.md) | The charge quantity changing history of the current rate plan charge in the current ramp interval. | [optional] 
**product_rate_plan_charge_id** | **str** | The ID of the corresponding product rate plan charge. | [optional] 
**subscription_number** | **str** | The number of the subscription that the current rate plan charge belongs to. | [optional] 

## Example

```python
from zuora_sdk.models.ramp_interval_charge_delta_metrics import RampIntervalChargeDeltaMetrics

# TODO update the JSON string below
json = "{}"
# create an instance of RampIntervalChargeDeltaMetrics from a JSON string
ramp_interval_charge_delta_metrics_instance = RampIntervalChargeDeltaMetrics.from_json(json)
# print the JSON string representation of the object
print(RampIntervalChargeDeltaMetrics.to_json())

# convert the object into a dict
ramp_interval_charge_delta_metrics_dict = ramp_interval_charge_delta_metrics_instance.to_dict()
# create an instance of RampIntervalChargeDeltaMetrics from a dict
ramp_interval_charge_delta_metrics_from_dict = RampIntervalChargeDeltaMetrics.from_dict(ramp_interval_charge_delta_metrics_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


