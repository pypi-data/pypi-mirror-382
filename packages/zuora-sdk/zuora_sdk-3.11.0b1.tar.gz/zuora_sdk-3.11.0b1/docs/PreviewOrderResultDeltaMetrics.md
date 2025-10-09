# PreviewOrderResultDeltaMetrics

**Note:** As of Zuora Billing Release 306, Zuora has upgraded the methodologies for calculating metrics in [Orders](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders). The new methodologies are reflected in the following Order Delta Metrics objects.   * [Order Delta Mrr](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/Order_Delta_Metrics/Order_Delta_Mrr)  * [Order Delta Tcv](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/Order_Delta_Metrics/Order_Delta_Tcv)  * [Order Delta Tcb](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/Order_Delta_Metrics/Order_Delta_Tcb)   It is recommended that all customers use the new [Order Delta Metrics](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/Order_Delta_Metrics/AA_Overview_of_Order_Delta_Metrics). If you are an existing [Order Metrics](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/AA_Overview_of_Orders/Key_Metrics_for_Orders) customer and want to migrate to Order Delta Metrics, submit a request at [Zuora Global Support](https://support.zuora.com/).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**order_delta_mrr** | [**List[OrderDeltaMrr]**](OrderDeltaMrr.md) |  | [optional] 
**order_delta_tcb** | [**List[OrderDeltaTcb]**](OrderDeltaTcb.md) |  | [optional] 
**order_delta_tcv** | [**List[OrderDeltaTcv]**](OrderDeltaTcv.md) |  | [optional] 
**order_delta_qty** | [**List[OrderDeltaQty]**](OrderDeltaQty.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.preview_order_result_delta_metrics import PreviewOrderResultDeltaMetrics

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewOrderResultDeltaMetrics from a JSON string
preview_order_result_delta_metrics_instance = PreviewOrderResultDeltaMetrics.from_json(json)
# print the JSON string representation of the object
print(PreviewOrderResultDeltaMetrics.to_json())

# convert the object into a dict
preview_order_result_delta_metrics_dict = preview_order_result_delta_metrics_instance.to_dict()
# create an instance of PreviewOrderResultDeltaMetrics from a dict
preview_order_result_delta_metrics_from_dict = PreviewOrderResultDeltaMetrics.from_dict(preview_order_result_delta_metrics_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


