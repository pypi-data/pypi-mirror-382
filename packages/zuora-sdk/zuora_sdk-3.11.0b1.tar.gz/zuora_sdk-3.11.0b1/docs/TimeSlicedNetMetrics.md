# TimeSlicedNetMetrics


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **float** |  | [optional] 
**discount_charge_number** | **str** |  | [optional] 
**end_date** | **date** |  | [optional] 
**generated_reason** | [**TimeSlicedNetMetricsGeneratedReason**](TimeSlicedNetMetricsGeneratedReason.md) |  | [optional] 
**invoice_owner** | **str** | The acount number of the billing account that is billed for the subscription. | [optional] 
**order_item_id** | **str** | The ID of the order item referenced by the order metrics.  This field is only available to existing Orders customers who already have access to the field.  **Note:** The following Order Metrics have been deprecated. Any new customers who onboard on [Orders](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/AA_Overview_of_Orders) or [Orders Harmonization](https://knowledgecenter.zuora.com/Billing/Subscriptions/Orders/Orders_Harmonization/Orders_Harmonization) will not get these metrics. * The Order ELP and Order Item objects  * The \&quot;Generated Reason\&quot; and \&quot;Order Item ID\&quot; fields in the Order MRR, Order TCB, Order TCV, and Order Quantity objects  Existing Orders customers who have these metrics will continue to be supported.  | [optional] 
**start_date** | **date** |  | [optional] 
**subscription_owner** | **str** | The acount number of the billing account that owns the subscription. | [optional] 
**term_number** | **int** |  | [optional] 
**type** | [**TimeSlicedNetMetricsType**](TimeSlicedNetMetricsType.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.time_sliced_net_metrics import TimeSlicedNetMetrics

# TODO update the JSON string below
json = "{}"
# create an instance of TimeSlicedNetMetrics from a JSON string
time_sliced_net_metrics_instance = TimeSlicedNetMetrics.from_json(json)
# print the JSON string representation of the object
print(TimeSlicedNetMetrics.to_json())

# convert the object into a dict
time_sliced_net_metrics_dict = time_sliced_net_metrics_instance.to_dict()
# create an instance of TimeSlicedNetMetrics from a dict
time_sliced_net_metrics_from_dict = TimeSlicedNetMetrics.from_dict(time_sliced_net_metrics_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


