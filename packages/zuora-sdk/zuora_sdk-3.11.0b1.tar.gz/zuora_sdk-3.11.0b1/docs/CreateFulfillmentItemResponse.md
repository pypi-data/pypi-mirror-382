# CreateFulfillmentItemResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The sytem generated Id.  | [optional] 

## Example

```python
from zuora_sdk.models.create_fulfillment_item_response import CreateFulfillmentItemResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateFulfillmentItemResponse from a JSON string
create_fulfillment_item_response_instance = CreateFulfillmentItemResponse.from_json(json)
# print the JSON string representation of the object
print(CreateFulfillmentItemResponse.to_json())

# convert the object into a dict
create_fulfillment_item_response_dict = create_fulfillment_item_response_instance.to_dict()
# create an instance of CreateFulfillmentItemResponse from a dict
create_fulfillment_item_response_from_dict = CreateFulfillmentItemResponse.from_dict(create_fulfillment_item_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


