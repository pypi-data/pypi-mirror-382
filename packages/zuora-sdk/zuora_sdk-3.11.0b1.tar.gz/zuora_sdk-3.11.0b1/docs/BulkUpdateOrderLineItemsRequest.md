# BulkUpdateOrderLineItemsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**order_line_items** | [**List[BulkUpdateOrderLineItem]**](BulkUpdateOrderLineItem.md) |  | [optional] 
**processing_options** | [**ProcessingOptions**](ProcessingOptions.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.bulk_update_order_line_items_request import BulkUpdateOrderLineItemsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of BulkUpdateOrderLineItemsRequest from a JSON string
bulk_update_order_line_items_request_instance = BulkUpdateOrderLineItemsRequest.from_json(json)
# print the JSON string representation of the object
print(BulkUpdateOrderLineItemsRequest.to_json())

# convert the object into a dict
bulk_update_order_line_items_request_dict = bulk_update_order_line_items_request_instance.to_dict()
# create an instance of BulkUpdateOrderLineItemsRequest from a dict
bulk_update_order_line_items_request_from_dict = BulkUpdateOrderLineItemsRequest.from_dict(bulk_update_order_line_items_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


