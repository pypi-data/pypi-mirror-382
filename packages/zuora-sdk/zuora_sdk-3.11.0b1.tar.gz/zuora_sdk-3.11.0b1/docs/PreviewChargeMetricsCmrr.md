# PreviewChargeMetricsCmrr


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**discount** | **float** | Total discountCmrr of all discount charges which are applied to one specific recurring charge. This value is calculated from the rating results for the latest subscription version in the order. Only selects the applied discount charge when its endDateCondition is \&quot;Subscription_End\&quot;. | [optional] 
**discount_delta** | **float** | Delta discountCmrr value between the order base and the latest subscription version. | [optional] 
**regular** | **float** |  | [optional] 
**regular_delta** | **float** |  | [optional] 

## Example

```python
from zuora_sdk.models.preview_charge_metrics_cmrr import PreviewChargeMetricsCmrr

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewChargeMetricsCmrr from a JSON string
preview_charge_metrics_cmrr_instance = PreviewChargeMetricsCmrr.from_json(json)
# print the JSON string representation of the object
print(PreviewChargeMetricsCmrr.to_json())

# convert the object into a dict
preview_charge_metrics_cmrr_dict = preview_charge_metrics_cmrr_instance.to_dict()
# create an instance of PreviewChargeMetricsCmrr from a dict
preview_charge_metrics_cmrr_from_dict = PreviewChargeMetricsCmrr.from_dict(preview_charge_metrics_cmrr_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


