# CustomObjectBulkJobResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_by_id** | **str** | The ID of the user who creates the job. | [optional] 
**created_date** | **datetime** | The time when the bulk job is created. | [optional] 
**id** | **str** | The custom object bulk job ID. | [optional] 
**updated_by_id** | **str** | The ID of the user who updates the job. | [optional] 
**updated_date** | **datetime** | The time when the bulk job is updated. | [optional] 
**error** | [**CustomObjectBulkJobResponseError**](CustomObjectBulkJobResponseError.md) |  | [optional] 
**namespace** | [**CustomObjectBulkJobResponseNamespace**](CustomObjectBulkJobResponseNamespace.md) |  | [optional] 
**object** | **str** | The object to that the bulk operation performs on. | [optional] 
**operation** | [**CustomObjectBulkJobResponseOperation**](CustomObjectBulkJobResponseOperation.md) |  | [optional] 
**processing_time** | **int** | The amount of time elapsed, in milliseconds, from the submission to the completion of the bulk job. | [optional] 
**records_processed** | **int** | The number of object records processed by the bulk job. | [optional] 
**status** | [**CustomObjectBulkJobResponseStatus**](CustomObjectBulkJobResponseStatus.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.custom_object_bulk_job_response import CustomObjectBulkJobResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CustomObjectBulkJobResponse from a JSON string
custom_object_bulk_job_response_instance = CustomObjectBulkJobResponse.from_json(json)
# print the JSON string representation of the object
print(CustomObjectBulkJobResponse.to_json())

# convert the object into a dict
custom_object_bulk_job_response_dict = custom_object_bulk_job_response_instance.to_dict()
# create an instance of CustomObjectBulkJobResponse from a dict
custom_object_bulk_job_response_from_dict = CustomObjectBulkJobResponse.from_dict(custom_object_bulk_job_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


