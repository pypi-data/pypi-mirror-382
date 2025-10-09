# OrderActionRatePlanUpdate

Information about an order action of type `UpdateProduct`. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**charge_updates** | [**List[OrderActionRatePlanChargeUpdate]**](OrderActionRatePlanChargeUpdate.md) |  | [optional] 
**custom_fields** | **Dict[str, object]** | Container for custom fields of a Rate Plan object.  | [optional] 
**new_rate_plan_id** | **str** | Internal identifier of the updated rate plan in the new subscription version. | [optional] 
**rate_plan_id** | **str** | Internal identifier of the rate plan that was updated.  | [optional] 
**specific_update_date** | **date** |  The date when the Update Product order action takes effect. This field is only applicable if there is already a future-dated Update Product order action on the subscription. The format of the date is yyyy-mm-dd.  See [Update a Product on Subscription with Future-dated Updates](https://knowledgecenter.zuora.com/BC_Subscription_Management/Orders/AC_Orders_Tutorials/C_Update_a_Product_in_a_Subscription/Update_a_Product_on_Subscription_with_Future-dated_Updates) for more information about this feature.  | [optional] 
**unique_token** | **str** | A unique string to represent the rate plan charge in the order. The unique token is used to perform multiple actions against a newly added rate plan. For example, if you want to add and update a product in the same order, you would assign a unique token to the product rate plan when added and use that token in future order actions. | [optional] 

## Example

```python
from zuora_sdk.models.order_action_rate_plan_update import OrderActionRatePlanUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of OrderActionRatePlanUpdate from a JSON string
order_action_rate_plan_update_instance = OrderActionRatePlanUpdate.from_json(json)
# print the JSON string representation of the object
print(OrderActionRatePlanUpdate.to_json())

# convert the object into a dict
order_action_rate_plan_update_dict = order_action_rate_plan_update_instance.to_dict()
# create an instance of OrderActionRatePlanUpdate from a dict
order_action_rate_plan_update_from_dict = OrderActionRatePlanUpdate.from_dict(order_action_rate_plan_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


