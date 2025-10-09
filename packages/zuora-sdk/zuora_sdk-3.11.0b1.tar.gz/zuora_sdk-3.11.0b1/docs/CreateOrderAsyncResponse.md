# CreateOrderAsyncResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job_id** | **str** | The ID of an asynchronous job that will be returned for tracking the status and result of the job. | [optional] 
**success** | **bool** | Indicates whether the operation call succeeded. | [optional] 

## Example

```python
from zuora_sdk.models.create_order_async_response import CreateOrderAsyncResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CreateOrderAsyncResponse from a JSON string
create_order_async_response_instance = CreateOrderAsyncResponse.from_json(json)
# print the JSON string representation of the object
print(CreateOrderAsyncResponse.to_json())

# convert the object into a dict
create_order_async_response_dict = create_order_async_response_instance.to_dict()
# create an instance of CreateOrderAsyncResponse from a dict
create_order_async_response_from_dict = CreateOrderAsyncResponse.from_dict(create_order_async_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


