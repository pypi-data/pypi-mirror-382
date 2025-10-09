# GetOrderLineItemResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**order_line_item** | [**GetOrderLineItem**](GetOrderLineItem.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.get_order_line_item_response import GetOrderLineItemResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetOrderLineItemResponse from a JSON string
get_order_line_item_response_instance = GetOrderLineItemResponse.from_json(json)
# print the JSON string representation of the object
print(GetOrderLineItemResponse.to_json())

# convert the object into a dict
get_order_line_item_response_dict = get_order_line_item_response_instance.to_dict()
# create an instance of GetOrderLineItemResponse from a dict
get_order_line_item_response_from_dict = GetOrderLineItemResponse.from_dict(get_order_line_item_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


