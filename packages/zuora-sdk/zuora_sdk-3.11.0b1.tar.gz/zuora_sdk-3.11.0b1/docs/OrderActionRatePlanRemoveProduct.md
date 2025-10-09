# OrderActionRatePlanRemoveProduct

Information about an order action of type `RemoveProduct`. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**rate_plan_id** | **str** | Internal identifier of the rate plan to remove.  | [optional] 
**unique_token** | **str** | A unique string to represent the rate plan charge in the order. The unique token is used to perform multiple actions against a newly added rate plan. For example, if you want to add and update a product in the same order, you would assign a unique token to the product rate plan when added and use that token in future order actions.A unique string in the order to represent the rate plan. | [optional] 

## Example

```python
from zuora_sdk.models.order_action_rate_plan_remove_product import OrderActionRatePlanRemoveProduct

# TODO update the JSON string below
json = "{}"
# create an instance of OrderActionRatePlanRemoveProduct from a JSON string
order_action_rate_plan_remove_product_instance = OrderActionRatePlanRemoveProduct.from_json(json)
# print the JSON string representation of the object
print(OrderActionRatePlanRemoveProduct.to_json())

# convert the object into a dict
order_action_rate_plan_remove_product_dict = order_action_rate_plan_remove_product_instance.to_dict()
# create an instance of OrderActionRatePlanRemoveProduct from a dict
order_action_rate_plan_remove_product_from_dict = OrderActionRatePlanRemoveProduct.from_dict(order_action_rate_plan_remove_product_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


