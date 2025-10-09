# CreateFulfillmentResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**fulfillment_items** | [**List[CreateFulfillmentItemResponse]**](CreateFulfillmentItemResponse.md) |  | [optional] 
**fulfillment_number** | **str** | The sytem generated number for the Fulfillment.  | [optional] 
**id** | **str** | The sytem generated Id.  | [optional] 

## Example

```python
from zuora_sdk.models.create_fulfillment_response import CreateFulfillmentResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateFulfillmentResponse from a JSON string
create_fulfillment_response_instance = CreateFulfillmentResponse.from_json(json)
# print the JSON string representation of the object
print(CreateFulfillmentResponse.to_json())

# convert the object into a dict
create_fulfillment_response_dict = create_fulfillment_response_instance.to_dict()
# create an instance of CreateFulfillmentResponse from a dict
create_fulfillment_response_from_dict = CreateFulfillmentResponse.from_dict(create_fulfillment_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


