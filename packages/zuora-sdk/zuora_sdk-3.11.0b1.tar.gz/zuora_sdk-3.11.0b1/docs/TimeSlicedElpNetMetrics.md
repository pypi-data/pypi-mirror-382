# TimeSlicedElpNetMetrics


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** | The extended list price which is calculated by the original product catalog list price multiplied by the delta quantity. | [optional] 
**end_date** | **date** | The latest date that the metric applies. | [optional] 
**generated_reason** | [**TimeSlicedElpNetMetricsGeneratedReason**](TimeSlicedElpNetMetricsGeneratedReason.md) |  | [optional] 
**invoice_owner** | **str** | The acount number of the billing account that is billed for the subscription. | [optional] 
**order_item_id** | **str** | The ID of the order item referenced by the order metrics. | [optional] 
**start_date** | **date** | The earliest date that the metric applies. | [optional] 
**subscription_owner** | **str** | The acount number of the billing account that owns the subscription. | [optional] 
**tax** | **float** | The tax amount in the metric when the tax permission is enabled. | [optional] 
**term_number** | **int** |  | [optional] 
**type** | [**TimeSlicedElpNetMetricsType**](TimeSlicedElpNetMetricsType.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.time_sliced_elp_net_metrics import TimeSlicedElpNetMetrics

# TODO update the JSON string below
json = "{}"
# create an instance of TimeSlicedElpNetMetrics from a JSON string
time_sliced_elp_net_metrics_instance = TimeSlicedElpNetMetrics.from_json(json)
# print the JSON string representation of the object
print(TimeSlicedElpNetMetrics.to_json())

# convert the object into a dict
time_sliced_elp_net_metrics_dict = time_sliced_elp_net_metrics_instance.to_dict()
# create an instance of TimeSlicedElpNetMetrics from a dict
time_sliced_elp_net_metrics_from_dict = TimeSlicedElpNetMetrics.from_dict(time_sliced_elp_net_metrics_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


