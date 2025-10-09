# ExpandedFulfillment


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | [optional] 
**created_by_id** | **str** |  | [optional] 
**created_date** | **str** |  | [optional] 
**updated_by_id** | **str** |  | [optional] 
**updated_date** | **str** |  | [optional] 
**order_line_item_id** | **str** |  | [optional] 
**fulfillment_number** | **str** |  | [optional] 
**fulfillment_date** | **date** |  | [optional] 
**fulfillment_type** | **str** |  | [optional] 
**quantity** | **float** |  | [optional] 
**state** | **str** |  | [optional] 
**bill_target_date** | **date** |  | [optional] 
**description** | **str** |  | [optional] 
**tracking_number** | **str** |  | [optional] 
**carrier** | **str** |  | [optional] 
**fulfillment_system** | **str** |  | [optional] 
**fulfillment_location** | **str** |  | [optional] 
**external_id** | **str** |  | [optional] 
**exclude_item_booking_from_revenue_accounting** | **bool** |  | [optional] 
**exclude_item_billing_from_revenue_accounting** | **bool** |  | [optional] 

## Example

```python
from zuora_sdk.models.expanded_fulfillment import ExpandedFulfillment

# TODO update the JSON string below
json = "{}"
# create an instance of ExpandedFulfillment from a JSON string
expanded_fulfillment_instance = ExpandedFulfillment.from_json(json)
# print the JSON string representation of the object
print(ExpandedFulfillment.to_json())

# convert the object into a dict
expanded_fulfillment_dict = expanded_fulfillment_instance.to_dict()
# create an instance of ExpandedFulfillment from a dict
expanded_fulfillment_from_dict = ExpandedFulfillment.from_dict(expanded_fulfillment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


