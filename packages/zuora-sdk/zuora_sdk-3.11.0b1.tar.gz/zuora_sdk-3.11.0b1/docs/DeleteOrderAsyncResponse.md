# DeleteOrderAsyncResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job_id** | **str** | The ID of an asynchronous job that will be returned for tracking the status and result of the job. | [optional] 
**success** | **bool** | Indicates whether the operation call succeeded. | [optional] 

## Example

```python
from zuora_sdk.models.delete_order_async_response import DeleteOrderAsyncResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DeleteOrderAsyncResponse from a JSON string
delete_order_async_response_instance = DeleteOrderAsyncResponse.from_json(json)
# print the JSON string representation of the object
print(DeleteOrderAsyncResponse.to_json())

# convert the object into a dict
delete_order_async_response_dict = delete_order_async_response_instance.to_dict()
# create an instance of DeleteOrderAsyncResponse from a dict
delete_order_async_response_from_dict = DeleteOrderAsyncResponse.from_dict(delete_order_async_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


