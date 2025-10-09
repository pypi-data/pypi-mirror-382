# RampIntervalChargeMetricsMrrInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**discount** | **float** | The discount amount for the MRR. | [optional] 
**end_date** | **date** | The end date. | [optional] 
**gross** | **float** | The gross MRR amount before discounts charges are applied. | [optional] 
**net** | **float** | The net MRR amount after discounts charges are applied. | [optional] 
**start_date** | **date** | The start date. | [optional] 

## Example

```python
from zuora_sdk.models.ramp_interval_charge_metrics_mrr_inner import RampIntervalChargeMetricsMrrInner

# TODO update the JSON string below
json = "{}"
# create an instance of RampIntervalChargeMetricsMrrInner from a JSON string
ramp_interval_charge_metrics_mrr_inner_instance = RampIntervalChargeMetricsMrrInner.from_json(json)
# print the JSON string representation of the object
print(RampIntervalChargeMetricsMrrInner.to_json())

# convert the object into a dict
ramp_interval_charge_metrics_mrr_inner_dict = ramp_interval_charge_metrics_mrr_inner_instance.to_dict()
# create an instance of RampIntervalChargeMetricsMrrInner from a dict
ramp_interval_charge_metrics_mrr_inner_from_dict = RampIntervalChargeMetricsMrrInner.from_dict(ramp_interval_charge_metrics_mrr_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


