# AsyncOperationResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**id** | **str** | The ID of the business object which is being operated. | [optional] 
**job_id** | **str** | The ID of the operation job. | [optional] 
**job_status** | [**OperationJobStatus**](OperationJobStatus.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.async_operation_response import AsyncOperationResponse

# TODO update the JSON string below
json = "{}"
# create an instance of AsyncOperationResponse from a JSON string
async_operation_response_instance = AsyncOperationResponse.from_json(json)
# print the JSON string representation of the object
print(AsyncOperationResponse.to_json())

# convert the object into a dict
async_operation_response_dict = async_operation_response_instance.to_dict()
# create an instance of AsyncOperationResponse from a dict
async_operation_response_from_dict = AsyncOperationResponse.from_dict(async_operation_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


