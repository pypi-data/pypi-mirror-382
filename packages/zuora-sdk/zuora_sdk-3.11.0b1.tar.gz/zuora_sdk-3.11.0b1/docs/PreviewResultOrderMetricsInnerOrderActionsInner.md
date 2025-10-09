# PreviewResultOrderMetricsInnerOrderActionsInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**order_items** | [**List[OrderItem]**](OrderItem.md) | The &#x60;orderItems&#x60; nested field is only available to existing Orders customers who already have access to the field.   **Note:** The following Order Metrics have been deprecated. Any new customers who onboard on [Orders](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/AA_Overview_of_Orders) or [Orders Harmonization](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/Orders_Harmonization/Orders_Harmonization) will not get these metrics.  * The Order ELP and Order Item objects   * The \&quot;Generated Reason\&quot; and \&quot;Order Item ID\&quot; fields in the Order MRR, Order TCB, Order TCV, and Order Quantity objects   Existing Orders customers who have these metrics will continue to be supported. | [optional] 
**order_metrics** | [**List[OrderMetric]**](OrderMetric.md) | The container for order metrics.   **Note:** The following Order Metrics have been deprecated. Any new customers who onboard on [Orders](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/AA_Overview_of_Orders) or [Orders Harmonization](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/Orders_Harmonization/Orders_Harmonization) will not get these metrics.  * The Order ELP and Order Item objects   * The \&quot;Generated Reason\&quot; and \&quot;Order Item ID\&quot; fields in the Order MRR, Order TCB, Order TCV, and Order Quantity objects   Existing Orders customers who have these metrics will continue to be supported. | [optional] 
**sequence** | **str** |  | [optional] 
**type** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.preview_result_order_metrics_inner_order_actions_inner import PreviewResultOrderMetricsInnerOrderActionsInner

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewResultOrderMetricsInnerOrderActionsInner from a JSON string
preview_result_order_metrics_inner_order_actions_inner_instance = PreviewResultOrderMetricsInnerOrderActionsInner.from_json(json)
# print the JSON string representation of the object
print(PreviewResultOrderMetricsInnerOrderActionsInner.to_json())

# convert the object into a dict
preview_result_order_metrics_inner_order_actions_inner_dict = preview_result_order_metrics_inner_order_actions_inner_instance.to_dict()
# create an instance of PreviewResultOrderMetricsInnerOrderActionsInner from a dict
preview_result_order_metrics_inner_order_actions_inner_from_dict = PreviewResultOrderMetricsInnerOrderActionsInner.from_dict(preview_result_order_metrics_inner_order_actions_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


