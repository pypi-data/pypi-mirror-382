# RampIntervalChargeMetrics


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**charge_number** | **str** | The number of the charge. | [optional] 
**discount_tcb** | **float** | The discount amount for the TCB. | [optional] 
**discount_tcv** | **float** | The discount amount for the TCV. | [optional] 
**end_date** | **date** | The end date of the rate plan charge in the current ramp interval. | [optional] 
**gross_tcb** | **float** | The gross TCB value before discount charges are applied. | [optional] 
**gross_tcv** | **float** | The gross TCV value before discount charges are applied. | [optional] 
**mrr** | [**List[RampIntervalChargeMetricsMrrInner]**](RampIntervalChargeMetricsMrrInner.md) | The MRR changing history of the current rate plan charge in the current ramp interval. | [optional] 
**net_tcb** | **float** | The net TCB value after discount charges are applied. | [optional] 
**net_tcv** | **float** | The net TCV value after discount charges are applied. | [optional] 
**product_rate_plan_charge_id** | **str** | The ID of the corresponding product rate plan charge. | [optional] 
**quantity** | **float** | The quantity of the rate plan charge. | [optional] 
**rate_plan_charge_id** | **str** | The ID of the rate plan charge. | [optional] 
**start_date** | **date** | The start date of the rate plan charge in the current ramp interval. | [optional] 
**subscription_number** | **str** | The number of the subscription that the current rate plan charge belongs to. | [optional] 

## Example

```python
from zuora_sdk.models.ramp_interval_charge_metrics import RampIntervalChargeMetrics

# TODO update the JSON string below
json = "{}"
# create an instance of RampIntervalChargeMetrics from a JSON string
ramp_interval_charge_metrics_instance = RampIntervalChargeMetrics.from_json(json)
# print the JSON string representation of the object
print(RampIntervalChargeMetrics.to_json())

# convert the object into a dict
ramp_interval_charge_metrics_dict = ramp_interval_charge_metrics_instance.to_dict()
# create an instance of RampIntervalChargeMetrics from a dict
ramp_interval_charge_metrics_from_dict = RampIntervalChargeMetrics.from_dict(ramp_interval_charge_metrics_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


