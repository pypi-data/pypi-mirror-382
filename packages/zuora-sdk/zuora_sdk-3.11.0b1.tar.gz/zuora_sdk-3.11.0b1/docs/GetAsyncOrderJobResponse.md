# GetAsyncOrderJobResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**errors** | **str** | Error messages returned if the job failed. | [optional] 
**result** | [**GetAsyncOrderJobResponseResult**](GetAsyncOrderJobResponseResult.md) |  | [optional] 
**status** | [**JobStatus**](JobStatus.md) |  | [optional] 
**success** | **bool** | Indicates whether the operation call succeeded. | [optional] 

## Example

```python
from zuora_sdk.models.get_async_order_job_response import GetAsyncOrderJobResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetAsyncOrderJobResponse from a JSON string
get_async_order_job_response_instance = GetAsyncOrderJobResponse.from_json(json)
# print the JSON string representation of the object
print(GetAsyncOrderJobResponse.to_json())

# convert the object into a dict
get_async_order_job_response_dict = get_async_order_job_response_instance.to_dict()
# create an instance of GetAsyncOrderJobResponse from a dict
get_async_order_job_response_from_dict = GetAsyncOrderJobResponse.from_dict(get_async_order_job_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


