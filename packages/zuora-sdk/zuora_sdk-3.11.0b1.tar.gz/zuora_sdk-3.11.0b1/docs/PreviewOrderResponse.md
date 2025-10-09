# PreviewOrderResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**preview_result** | [**PreviewOrderResult**](PreviewOrderResult.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.preview_order_response import PreviewOrderResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewOrderResponse from a JSON string
preview_order_response_instance = PreviewOrderResponse.from_json(json)
# print the JSON string representation of the object
print(PreviewOrderResponse.to_json())

# convert the object into a dict
preview_order_response_dict = preview_order_response_instance.to_dict()
# create an instance of PreviewOrderResponse from a dict
preview_order_response_from_dict = PreviewOrderResponse.from_dict(preview_order_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


