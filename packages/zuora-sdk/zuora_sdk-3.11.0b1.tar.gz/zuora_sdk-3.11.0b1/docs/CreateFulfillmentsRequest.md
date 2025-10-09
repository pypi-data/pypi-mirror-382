# CreateFulfillmentsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**fulfillments** | [**List[CreateFulfillment]**](CreateFulfillment.md) |  | [optional] 
**processing_options** | [**ProcessingOptions**](ProcessingOptions.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.create_fulfillments_request import CreateFulfillmentsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateFulfillmentsRequest from a JSON string
create_fulfillments_request_instance = CreateFulfillmentsRequest.from_json(json)
# print the JSON string representation of the object
print(CreateFulfillmentsRequest.to_json())

# convert the object into a dict
create_fulfillments_request_dict = create_fulfillments_request_instance.to_dict()
# create an instance of CreateFulfillmentsRequest from a dict
create_fulfillments_request_from_dict = CreateFulfillmentsRequest.from_dict(create_fulfillments_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


