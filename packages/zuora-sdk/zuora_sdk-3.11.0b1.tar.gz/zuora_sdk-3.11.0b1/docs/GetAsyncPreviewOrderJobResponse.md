# GetAsyncPreviewOrderJobResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**charge_metrics** | [**List[PreviewOrderResultChargeMetrics]**](PreviewOrderResultChargeMetrics.md) |  | [optional] 
**credit_memos** | [**List[PreviewOrderResultCreditMemos]**](PreviewOrderResultCreditMemos.md) | This field is only available if you have the Invoice Settlement feature enabled. | [optional] 
**invoices** | [**List[PreviewOrderResultInvoices]**](PreviewOrderResultInvoices.md) |  | [optional] 
**order_delta_metrics** | [**PreviewOrderResultDeltaMetrics**](PreviewOrderResultDeltaMetrics.md) |  | [optional] 
**order_metrics** | [**List[PreviewResultOrderMetricsInner]**](PreviewResultOrderMetricsInner.md) | **Note:** As of Zuora Billing Release 306, Zuora has upgraded the methodologies for calculating metrics in [Orders](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders). The new methodologies are reflected in the following Order Delta Metrics objects.    * [Order Delta Mrr](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/Order_Delta_Metrics/Order_Delta_Mrr)   * [Order Delta Tcv](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/Order_Delta_Metrics/Order_Delta_Tcv)   * [Order Delta Tcb](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/Order_Delta_Metrics/Order_Delta_Tcb)    It is recommended that all customers use the new [Order Delta Metrics](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/Order_Delta_Metrics/AA_Overview_of_Order_Delta_Metrics). If you are an existing [Order Metrics](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/AA_Overview_of_Orders/Key_Metrics_for_Orders) customer and want to migrate to Order Delta Metrics, submit a request at [Zuora Global Support](https://support.zuora.com/).    Whereas new customers, and existing customers not currently on [Order Metrics](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/AA_Overview_of_Orders/Key_Metrics_for_Orders), will no longer have access to Order Metrics, existing customers currently using Order Metrics will continue to be supported. | [optional] 
**ramp_metrics** | [**List[OrderRampMetrics]**](OrderRampMetrics.md) | **Note**: This field is only available if you have the Ramps feature enabled. The [Orders](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/AA_Overview_of_Orders) feature must be enabled before you can access the [Ramps](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/Ramps_and_Ramp_Metrics/A_Overview_of_Ramps_and_Ramp_Metrics) feature. The Ramps feature is available for customers with Enterprise and Nine editions by default. If you are a Growth customer, see [Zuora Editions](https://knowledgecenter.zuora.com/BB_Introducing_Z_Business/C_Zuora_Editions) for pricing information coming October 2020.   The ramp metrics. | [optional] 
**job_type** | **str** | The type of job. | [default to 'AsyncPreviewOrder']

## Example

```python
from zuora_sdk.models.get_async_preview_order_job_response import GetAsyncPreviewOrderJobResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetAsyncPreviewOrderJobResponse from a JSON string
get_async_preview_order_job_response_instance = GetAsyncPreviewOrderJobResponse.from_json(json)
# print the JSON string representation of the object
print(GetAsyncPreviewOrderJobResponse.to_json())

# convert the object into a dict
get_async_preview_order_job_response_dict = get_async_preview_order_job_response_instance.to_dict()
# create an instance of GetAsyncPreviewOrderJobResponse from a dict
get_async_preview_order_job_response_from_dict = GetAsyncPreviewOrderJobResponse.from_dict(get_async_preview_order_job_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


