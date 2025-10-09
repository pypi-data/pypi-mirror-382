# PreviewResultOrderMetricsInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**order_actions** | [**List[PreviewResultOrderMetricsInnerOrderActionsInner]**](PreviewResultOrderMetricsInnerOrderActionsInner.md) |  | [optional] 
**subscription_number** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.preview_result_order_metrics_inner import PreviewResultOrderMetricsInner

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewResultOrderMetricsInner from a JSON string
preview_result_order_metrics_inner_instance = PreviewResultOrderMetricsInner.from_json(json)
# print the JSON string representation of the object
print(PreviewResultOrderMetricsInner.to_json())

# convert the object into a dict
preview_result_order_metrics_inner_dict = preview_result_order_metrics_inner_instance.to_dict()
# create an instance of PreviewResultOrderMetricsInner from a dict
preview_result_order_metrics_inner_from_dict = PreviewResultOrderMetricsInner.from_dict(preview_result_order_metrics_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


