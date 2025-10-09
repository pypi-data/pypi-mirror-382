# GetBulkUpdateOrderLineItemsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**order_line_items** | [**List[GetOrderLineItem]**](GetOrderLineItem.md) |  | [optional] 
**invoices** | **List[object]** |  | [optional] 

## Example

```python
from zuora_sdk.models.get_bulk_update_order_line_items_response import GetBulkUpdateOrderLineItemsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetBulkUpdateOrderLineItemsResponse from a JSON string
get_bulk_update_order_line_items_response_instance = GetBulkUpdateOrderLineItemsResponse.from_json(json)
# print the JSON string representation of the object
print(GetBulkUpdateOrderLineItemsResponse.to_json())

# convert the object into a dict
get_bulk_update_order_line_items_response_dict = get_bulk_update_order_line_items_response_instance.to_dict()
# create an instance of GetBulkUpdateOrderLineItemsResponse from a dict
get_bulk_update_order_line_items_response_from_dict = GetBulkUpdateOrderLineItemsResponse.from_dict(get_bulk_update_order_line_items_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


