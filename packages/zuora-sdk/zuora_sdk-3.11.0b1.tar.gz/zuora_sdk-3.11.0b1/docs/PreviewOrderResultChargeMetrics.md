# PreviewOrderResultChargeMetrics


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**charges** | [**List[PreviewChargeMetrics]**](PreviewChargeMetrics.md) |  | [optional] 
**subscription_number** | **str** | The number of the subscription that has been affected by this order. When creating a subscription, this value will not show if the subscription number was not specified in the request. | [optional] 

## Example

```python
from zuora_sdk.models.preview_order_result_charge_metrics import PreviewOrderResultChargeMetrics

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewOrderResultChargeMetrics from a JSON string
preview_order_result_charge_metrics_instance = PreviewOrderResultChargeMetrics.from_json(json)
# print the JSON string representation of the object
print(PreviewOrderResultChargeMetrics.to_json())

# convert the object into a dict
preview_order_result_charge_metrics_dict = preview_order_result_charge_metrics_instance.to_dict()
# create an instance of PreviewOrderResultChargeMetrics from a dict
preview_order_result_charge_metrics_from_dict = PreviewOrderResultChargeMetrics.from_dict(preview_order_result_charge_metrics_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


