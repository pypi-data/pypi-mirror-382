# PreviewChargeMetricsTcv


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**discount** | **float** | Always equals to discountTcb. | [optional] 
**discount_delta** | **float** | Always equals to delta discountTcb. | [optional] 
**regular** | **float** |  | [optional] 
**regular_delta** | **float** |  | [optional] 

## Example

```python
from zuora_sdk.models.preview_charge_metrics_tcv import PreviewChargeMetricsTcv

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewChargeMetricsTcv from a JSON string
preview_charge_metrics_tcv_instance = PreviewChargeMetricsTcv.from_json(json)
# print the JSON string representation of the object
print(PreviewChargeMetricsTcv.to_json())

# convert the object into a dict
preview_charge_metrics_tcv_dict = preview_charge_metrics_tcv_instance.to_dict()
# create an instance of PreviewChargeMetricsTcv from a dict
preview_charge_metrics_tcv_from_dict = PreviewChargeMetricsTcv.from_dict(preview_charge_metrics_tcv_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


