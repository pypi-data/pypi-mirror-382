# UpdateFulfillmentItemRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**custom_fields** | **Dict[str, object]** | Container for custom fields of a Fulfillment Item object.  | [optional] 
**description** | **str** | The description of the Fulfillment Item.  | [optional] 
**item_identifier** | **str** | The external identifier of the Fulfillment Item.  | [optional] 

## Example

```python
from zuora_sdk.models.update_fulfillment_item_request import UpdateFulfillmentItemRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateFulfillmentItemRequest from a JSON string
update_fulfillment_item_request_instance = UpdateFulfillmentItemRequest.from_json(json)
# print the JSON string representation of the object
print(UpdateFulfillmentItemRequest.to_json())

# convert the object into a dict
update_fulfillment_item_request_dict = update_fulfillment_item_request_instance.to_dict()
# create an instance of UpdateFulfillmentItemRequest from a dict
update_fulfillment_item_request_from_dict = UpdateFulfillmentItemRequest.from_dict(update_fulfillment_item_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


