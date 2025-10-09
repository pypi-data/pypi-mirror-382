# RampIntervalChargeDeltaMetricsDeltaQuantityInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The delta amount of the charge quantity. | [optional] 
**end_date** | **date** | The end date. | [optional] 
**start_date** | **date** | The start date. | [optional] 

## Example

```python
from zuora_sdk.models.ramp_interval_charge_delta_metrics_delta_quantity_inner import RampIntervalChargeDeltaMetricsDeltaQuantityInner

# TODO update the JSON string below
json = "{}"
# create an instance of RampIntervalChargeDeltaMetricsDeltaQuantityInner from a JSON string
ramp_interval_charge_delta_metrics_delta_quantity_inner_instance = RampIntervalChargeDeltaMetricsDeltaQuantityInner.from_json(json)
# print the JSON string representation of the object
print(RampIntervalChargeDeltaMetricsDeltaQuantityInner.to_json())

# convert the object into a dict
ramp_interval_charge_delta_metrics_delta_quantity_inner_dict = ramp_interval_charge_delta_metrics_delta_quantity_inner_instance.to_dict()
# create an instance of RampIntervalChargeDeltaMetricsDeltaQuantityInner from a dict
ramp_interval_charge_delta_metrics_delta_quantity_inner_from_dict = RampIntervalChargeDeltaMetricsDeltaQuantityInner.from_dict(ramp_interval_charge_delta_metrics_delta_quantity_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


