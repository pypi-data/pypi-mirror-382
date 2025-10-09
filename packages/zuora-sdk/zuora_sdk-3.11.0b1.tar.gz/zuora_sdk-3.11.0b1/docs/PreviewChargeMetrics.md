# PreviewChargeMetrics


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**charge_number** | **str** |  | [optional] 
**cmrr** | [**PreviewChargeMetricsCmrr**](PreviewChargeMetricsCmrr.md) |  | [optional] 
**origin_rate_plan_id** | **str** |  | [optional] 
**product_rate_plan_charge_id** | **str** |  | [optional] 
**product_rate_plan_id** | **str** |  | [optional] 
**subscription_rate_plan_number** | **str** |  | [optional] 
**is_pending** | **bool** |  | [optional] 
**tax** | [**PreviewChargeMetricsTax**](PreviewChargeMetricsTax.md) |  | [optional] 
**tcb** | [**PreviewChargeMetricsTcb**](PreviewChargeMetricsTcb.md) |  | [optional] 
**tcv** | [**PreviewChargeMetricsTcv**](PreviewChargeMetricsTcv.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.preview_charge_metrics import PreviewChargeMetrics

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewChargeMetrics from a JSON string
preview_charge_metrics_instance = PreviewChargeMetrics.from_json(json)
# print the JSON string representation of the object
print(PreviewChargeMetrics.to_json())

# convert the object into a dict
preview_charge_metrics_dict = preview_charge_metrics_instance.to_dict()
# create an instance of PreviewChargeMetrics from a dict
preview_charge_metrics_from_dict = PreviewChargeMetrics.from_dict(preview_charge_metrics_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


