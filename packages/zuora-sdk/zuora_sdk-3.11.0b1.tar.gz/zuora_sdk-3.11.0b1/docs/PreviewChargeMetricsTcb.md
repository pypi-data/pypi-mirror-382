# PreviewChargeMetricsTcb


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**discount** | **float** | Total contract billing amount of all discount charges which are applied to one specific recurring charge. This value is calculated from the rating results for the latest subscription version in the order. | [optional] 
**discount_delta** | **float** | Delta discount TCB value between the base and the latest subscription version for specific recurring charge in the order. | [optional] 
**regular** | **float** |  | [optional] 
**regular_delta** | **float** | Delta TCB value between the base and the latest subscription version in the order. | [optional] 

## Example

```python
from zuora_sdk.models.preview_charge_metrics_tcb import PreviewChargeMetricsTcb

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewChargeMetricsTcb from a JSON string
preview_charge_metrics_tcb_instance = PreviewChargeMetricsTcb.from_json(json)
# print the JSON string representation of the object
print(PreviewChargeMetricsTcb.to_json())

# convert the object into a dict
preview_charge_metrics_tcb_dict = preview_charge_metrics_tcb_instance.to_dict()
# create an instance of PreviewChargeMetricsTcb from a dict
preview_charge_metrics_tcb_from_dict = PreviewChargeMetricsTcb.from_dict(preview_charge_metrics_tcb_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


