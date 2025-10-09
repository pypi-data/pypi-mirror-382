# OperationJobResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**id** | **str** | The ID of the operation job to retrieve information about. | [optional] 
**object_id** | **str** | The ID of the business object which is being operated. | [optional] 
**object_type** | [**OperationJobObjectType**](OperationJobObjectType.md) |  | [optional] 
**operation_type** | [**OperationJobType**](OperationJobType.md) |  | [optional] 
**status** | [**OperationJobStatus**](OperationJobStatus.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.operation_job_response import OperationJobResponse

# TODO update the JSON string below
json = "{}"
# create an instance of OperationJobResponse from a JSON string
operation_job_response_instance = OperationJobResponse.from_json(json)
# print the JSON string representation of the object
print(OperationJobResponse.to_json())

# convert the object into a dict
operation_job_response_dict = operation_job_response_instance.to_dict()
# create an instance of OperationJobResponse from a dict
operation_job_response_from_dict = OperationJobResponse.from_dict(operation_job_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


