# CreateOrderResponseOrderMetric

The order metrics in create order response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**charge_number** | **str** |  | [optional] 
**mrr** | [**List[TimeSlicedNetMetrics]**](TimeSlicedNetMetrics.md) |  | [optional] 
**quantity** | [**List[TimeSlicedMetrics]**](TimeSlicedMetrics.md) |  | [optional] 
**tcb** | [**List[TimeSlicedTcbNetMetrics]**](TimeSlicedTcbNetMetrics.md) | Total contracted billing which is the forecast value for the total invoice amount. | [optional] 
**tcv** | [**List[TimeSlicedNetMetrics]**](TimeSlicedNetMetrics.md) | Total contracted value. | [optional] 

## Example

```python
from zuora_sdk.models.create_order_response_order_metric import CreateOrderResponseOrderMetric

# TODO update the JSON string below
json = "{}"
# create an instance of CreateOrderResponseOrderMetric from a JSON string
create_order_response_order_metric_instance = CreateOrderResponseOrderMetric.from_json(json)
# print the JSON string representation of the object
print(CreateOrderResponseOrderMetric.to_json())

# convert the object into a dict
create_order_response_order_metric_dict = create_order_response_order_metric_instance.to_dict()
# create an instance of CreateOrderResponseOrderMetric from a dict
create_order_response_order_metric_from_dict = CreateOrderResponseOrderMetric.from_dict(create_order_response_order_metric_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


