# Job


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Job id | [optional] 
**import_type** | [**JobType**](JobType.md) |  | [optional] 
**uploaded_file_id** | **str** | Id of uploaded file | [optional] 
**uploaded_file_name** | **str** | Name of uploaded file | [optional] 
**uploaded_file_url** | **str** |  | [optional] 
**uploaded_file_size** | **str** |  | [optional] 
**input_file_size** | **int** |  | [optional] 
**output_size** | **str** |  | [optional] 
**output_type** | **str** |  | [optional] 
**output_file_size** | **int** |  | [optional] 
**uploaded_by** | **str** |  | [optional] 
**uploaded_on** | **datetime** |  | [optional] 
**completed_on** | **datetime** |  | [optional] 
**started_processing_on** | **datetime** |  | [optional] 
**result_file_id** | **str** |  | [optional] 
**result_file_name** | **str** |  | [optional] 
**result_file_url** | **str** |  | [optional] 
**total_count** | **int** |  | [optional] 
**failed_count** | **int** |  | [optional] 
**status** | [**DataBackfillJobStatus**](DataBackfillJobStatus.md) |  | [optional] 
**failure_message** | **str** |  | [optional] 
**processed_count** | **int** |  | [optional] 
**success_count** | **int** |  | [optional] 
**remaining_time** | **int** |  | [optional] 
**remaining_time_text** | **str** |  | [optional] 
**completed_percentage** | **int** |  | [optional] 

## Example

```python
from zuora_sdk.models.job import Job

# TODO update the JSON string below
json = "{}"
# create an instance of Job from a JSON string
job_instance = Job.from_json(json)
# print the JSON string representation of the object
print(Job.to_json())

# convert the object into a dict
job_dict = job_instance.to_dict()
# create an instance of Job from a dict
job_from_dict = Job.from_dict(job_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


