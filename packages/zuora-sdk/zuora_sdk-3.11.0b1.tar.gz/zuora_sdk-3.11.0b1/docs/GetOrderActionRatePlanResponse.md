# GetOrderActionRatePlanResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**amendment** | [**OrderActionRatePlanAmendment**](OrderActionRatePlanAmendment.md) |  | [optional] 
**externally_managed_plan_id** | **str** | The unique identifier for the rate plan purchased on a third-party store. This field is used to represent a subscription rate plan created through third-party stores.  | [optional] 
**id** | **str** | Unique subscription rate-plan ID. | [optional] 
**last_change_type** | **str** | Latest change type. Possible values are:  - New - Update - Remove  | [optional] 
**order** | [**OrderActionRatePlanOrder**](OrderActionRatePlanOrder.md) |  | [optional] 
**product_id** | **str** | Product ID  | [optional] 
**product_name** | **str** | The name of the product.  | [optional] 
**product_rate_plan_id** | **str** | Product rate plan ID  | [optional] 
**product_sku** | **str** | The unique SKU for the product.  | [optional] 
**rate_plan_name** | **str** | The name of the rate plan.  | [optional] 
**subscription_id** | **str** | Subscription ID.  | [optional] 
**subscription_version** | **object** | The version of the subscription.  | [optional] 

## Example

```python
from zuora_sdk.models.get_order_action_rate_plan_response import GetOrderActionRatePlanResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetOrderActionRatePlanResponse from a JSON string
get_order_action_rate_plan_response_instance = GetOrderActionRatePlanResponse.from_json(json)
# print the JSON string representation of the object
print(GetOrderActionRatePlanResponse.to_json())

# convert the object into a dict
get_order_action_rate_plan_response_dict = get_order_action_rate_plan_response_instance.to_dict()
# create an instance of GetOrderActionRatePlanResponse from a dict
get_order_action_rate_plan_response_from_dict = GetOrderActionRatePlanResponse.from_dict(get_order_action_rate_plan_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


