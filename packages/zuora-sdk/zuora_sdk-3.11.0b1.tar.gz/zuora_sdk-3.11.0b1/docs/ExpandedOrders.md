# ExpandedOrders


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**order_date** | **date** |  | [optional] 
**order_number** | **str** |  | [optional] 
**account_id** | **str** |  | [optional] 
**status** | **str** |  | [optional] 
**state** | **str** |  | [optional] 
**created_by_migration** | **bool** |  | [optional] 
**category** | **str** |  | [optional] 
**invoice_schedule_id** | **str** |  | [optional] 
**scheduled_date** | **date** |  | [optional] 
**scheduled_date_policy** | **str** |  | [optional] 
**is_scheduled** | **bool** |  | [optional] 
**error_code** | **str** |  | [optional] 
**error_message** | **str** |  | [optional] 
**response** | **str** |  | [optional] 
**reverted_order_id** | **str** |  | [optional] 
**reverted_by_order_id** | **str** |  | [optional] 
**reverted_order_number** | **str** |  | [optional] 
**reversion_order** | **bool** |  | [optional] 
**reverted_date** | **date** |  | [optional] 
**cancel_reason** | **str** |  | [optional] 
**account** | [**ExpandedAccount**](ExpandedAccount.md) |  | [optional] 
**order_line_items** | [**List[ExpandedOrderLineItem]**](ExpandedOrderLineItem.md) |  | [optional] 
**order_actions** | [**List[ExpandedOrderAction]**](ExpandedOrderAction.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_orders import ExpandedOrders

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedOrders from a JSON string
expanded_orders_instance = ExpandedOrders.from_json(json)
# print the JSON string representation of the object
print(ExpandedOrders.to_json())

# convert the object into a dict
expanded_orders_dict = expanded_orders_instance.to_dict()
# create an instance of ExpandedOrders from a dict
expanded_orders_from_dict = ExpandedOrders.from_dict(expanded_orders_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


