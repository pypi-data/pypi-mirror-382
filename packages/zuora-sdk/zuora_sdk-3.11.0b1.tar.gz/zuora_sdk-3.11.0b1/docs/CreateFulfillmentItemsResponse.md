# CreateFulfillmentItemsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**fulfillment_items** | [**List[CreateFulfillmentItemResponse]**](CreateFulfillmentItemResponse.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.create_fulfillment_items_response import CreateFulfillmentItemsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateFulfillmentItemsResponse from a JSON string
create_fulfillment_items_response_instance = CreateFulfillmentItemsResponse.from_json(json)
# print the JSON string representation of the object
print(CreateFulfillmentItemsResponse.to_json())

# convert the object into a dict
create_fulfillment_items_response_dict = create_fulfillment_items_response_instance.to_dict()
# create an instance of CreateFulfillmentItemsResponse from a dict
create_fulfillment_items_response_from_dict = CreateFulfillmentItemsResponse.from_dict(create_fulfillment_items_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


