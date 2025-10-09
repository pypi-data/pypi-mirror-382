# CreateFulfillmentItemsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**fulfillment_items** | [**List[CreateFulfillmentItem]**](CreateFulfillmentItem.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.create_fulfillment_items_request import CreateFulfillmentItemsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateFulfillmentItemsRequest from a JSON string
create_fulfillment_items_request_instance = CreateFulfillmentItemsRequest.from_json(json)
# print the JSON string representation of the object
print(CreateFulfillmentItemsRequest.to_json())

# convert the object into a dict
create_fulfillment_items_request_dict = create_fulfillment_items_request_instance.to_dict()
# create an instance of CreateFulfillmentItemsRequest from a dict
create_fulfillment_items_request_from_dict = CreateFulfillmentItemsRequest.from_dict(create_fulfillment_items_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


