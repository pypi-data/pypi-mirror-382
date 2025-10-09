# OrderDeltaMetric


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**charge_number** | **str** | The charge number for the associated Rate Plan Charge. This field can be null if the metric is generated for an Order Line Item. | [optional] 
**currency** | **str** | ISO 3-letter currency code (uppercase). For example, USD.  | [optional] 
**end_date** | **date** | The end date for the order delta metric.  | [optional] 
**gross_amount** | **float** | The gross amount for the metric. The is the amount excluding applied discount. | [optional] 
**net_amount** | **float** | The net amount for the metric. The is the amount with discounts applied  | [optional] 
**order_action_id** | **str** | The Id for the related Order Action. This field can be null if the metric is generated for an Order Line Item. | [optional] 
**order_action_sequence** | **str** | The sequence for the related Order Action. This field can be null if the metric is generated for an Order Line Item. | [optional] 
**order_action_type** | **str** | The type for the related Order Action. This field can be null if the metric is generated for an Order Line Item. | [optional] 
**order_line_item_number** | **str** | A sequential number auto-assigned for each of order line items in a order, used as an index, for example, \&quot;1\&quot;. | [optional] 
**product_rate_plan_charge_id** | **str** | The Id for the associated Product Rate Plan Charge. This field can be null if the Order Line Item is not associated with a Product Rate Plan Charge. | [optional] 
**rate_plan_charge_id** | **str** | The id for the associated Rate Plan Charge. This field can be null if the metric is generated for an Order Line Item. | [optional] 
**start_date** | **date** | The start date for the order delta metric.  | [optional] 
**subscription_number** | **str** | The number of the subscription. This field can be null if the metric is generated for an Order Line Item. | [optional] 

## Example

```python
from zuora_sdk.models.order_delta_metric import OrderDeltaMetric

# TODO update the JSON string below
json = "{}"
# create an instance of OrderDeltaMetric from a JSON string
order_delta_metric_instance = OrderDeltaMetric.from_json(json)
# print the JSON string representation of the object
print(OrderDeltaMetric.to_json())

# convert the object into a dict
order_delta_metric_dict = order_delta_metric_instance.to_dict()
# create an instance of OrderDeltaMetric from a dict
order_delta_metric_from_dict = OrderDeltaMetric.from_dict(order_delta_metric_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


