# OrderDeltaQty

Order Delta Qty. This is a metric that reflects the change to the QTY on Rate Plan Charge object, or the Quantity for an Order Line Item as the result of the order

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**charge_number** | **str** | The charge number for the associated Rate Plan Charge. This field can be null if the metric is generated for an Order Line Item. | [optional] 
**end_date** | **date** | The end date for the order delta metric.  | [optional] 
**quantity** | **float** | The gross amount for the metric. The is the amount excluding applied discount. | [optional] 
**order_action_id** | **str** | The Id for the related Order Action. This field can be null if the metric is generated for an Order Line Item. | [optional] 
**order_action_sequence** | **str** | The sequence for the related Order Action. This field can be null if the metric is generated for an Order Line Item. | [optional] 
**order_action_type** | **str** | The type for the related Order Action. This field can be null if the metric is generated for an Order Line Item. | [optional] 
**order_line_item_number** | **str** | A sequential number auto-assigned for each of order line items in a order, used as an index, for example, \&quot;1\&quot;. | [optional] 
**product_rate_plan_charge_id** | **str** | The Id for the associated Product Rate Plan Charge. This field can be null if the Order Line Item is not associated with a Product Rate Plan Charge. | [optional] 
**rate_plan_charge_id** | **str** | The id for the associated Rate Plan Charge. This field can be null if the metric is generated for an Order Line Item. | [optional] 
**start_date** | **date** | The start date for the order delta metric.  | [optional] 
**subscription_number** | **str** | The number of the subscription. This field can be null if the metric is generated for an Order Line Item. | [optional] 
**order_line_item_id** | **str** | The system generated Id for the Order Line Item. This field can be null if the metric is generated for a Rate Plan Charge. | [optional] 

## Example

```python
from zuora_sdk.models.order_delta_qty import OrderDeltaQty

# TODO update the JSON string below
json = "{}"
# create an instance of OrderDeltaQty from a JSON string
order_delta_qty_instance = OrderDeltaQty.from_json(json)
# print the JSON string representation of the object
print(OrderDeltaQty.to_json())

# convert the object into a dict
order_delta_qty_dict = order_delta_qty_instance.to_dict()
# create an instance of OrderDeltaQty from a dict
order_delta_qty_from_dict = OrderDeltaQty.from_dict(order_delta_qty_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


