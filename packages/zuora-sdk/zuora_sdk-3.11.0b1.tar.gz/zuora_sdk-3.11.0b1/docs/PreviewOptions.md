# PreviewOptions


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**preview_number_of_periods** | **int** | The number of periods to preview when the value of the &#x60;previewThroughType&#x60; field is set to &#x60;NumberOfPeriods&#x60;.  | [optional] 
**preview_thru_type** | [**PreviewOptionsPreviewThruType**](PreviewOptionsPreviewThruType.md) |  | [optional] 
**preview_types** | **List[str]** | One or more types of the preview. It can include:  * ChargeMetrics: charge level metrics will be returned in the response, including: &#x60;cmrr&#x60;, &#x60;tcv&#x60;, &#x60;tcb&#x60;, and &#x60;tax&#x60;. * BillingDocs: &#x60;invoices&#x60; and &#x60;creditMemos&#x60; will be returned in the response. Note &#x60;creditMemos&#x60; is only available if the Invoice Settlement feature is enabled. * OrderDeltaMetrics: order delta metrics will be returned in the response, including: &#x60;orderDeltaMrr&#x60;, &#x60;orderDeltaTcb&#x60; and  &#x60;orderDeltaTcv&#x60;. * OrderMetrics: order metrics will be returned in the response, including: &#x60;quantity&#x60;, &#x60;mrr&#x60;, &#x60;tcb&#x60;, &#x60;tcv&#x60;, and &#x60;elp&#x60;. **Note:** As of Zuora Billing Release 306, Zuora has upgraded the methodologies for calculating metrics in [Orders](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders). The new methodologies are reflected in the OrderDeltaMetrics. It is recommended that all customers use the [Order Delta Metrics](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/Order_Delta_Metrics/AA_Overview_of_Order_Delta_Metrics). If you are an existing [Order Metrics](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/AA_Overview_of_Orders/Key_Metrics_for_Orders) customer and want to migrate to Order Delta Metrics, submit a request at [Zuora Global Support](https://support.zuora.com/). Whereas new customers, and existing customers not currently on [Order Metrics](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/AA_Overview_of_Orders/Key_Metrics_for_Orders), will no longer have access to Order Metrics, existing customers currently using Order Metrics will continue to be supported. * RampMetrics: ramp metrics will be returned in the response, including: &#x60;quantity&#x60;, &#x60;mrr&#x60;, &#x60;tcb&#x60;, &#x60;tcv&#x60; metrics for each charge and each ramp interval. * RampDeltaMetrics: ramp metrics changes will be returned in the response, including: &#x60;deltaQuantity&#x60;, &#x60;deltaMrr&#x60;, &#x60;deltaTcb&#x60;, &#x60;deltaTcv&#x60; metrics for each charge and each ramp interval.  | [optional] 
**specific_preview_thru_date** | **date** | The end date of the order preview. You can preview the invoice charges through the preview through date. (Invoice preview only)   **Note:** This field is only applicable if the &#39;previewThruType&#39; field is set to &#39;SpecificDate&#39;.  | [optional] 
**charge_type_to_exclude** | [**List[ChargeType]**](ChargeType.md) | The charge types to exclude from the forecast run. | [optional] 
**skip_tax** | **bool** | Whether to skip tax calculation during order preview. When set to &#x60;true&#x60;, tax calculation is bypassed and invoices will show zero tax amounts, which can significantly improve preview performance for customers using external tax engines.  **Priority Logic:** 1. Global tenant setting &#x60;PREVIEW_INVOICE_SKIP_TAX&#x60; takes highest priority and overrides this field 2. When not specified (null), defaults to normal tax calculation behavior  **Note:** This field works for all customers regardless of request source.  | [optional] 

## Example

```python
from zuora_sdk.models.preview_options import PreviewOptions

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewOptions from a JSON string
preview_options_instance = PreviewOptions.from_json(json)
# print the JSON string representation of the object
print(PreviewOptions.to_json())

# convert the object into a dict
preview_options_dict = preview_options_instance.to_dict()
# create an instance of PreviewOptions from a dict
preview_options_from_dict = PreviewOptions.from_dict(preview_options_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


