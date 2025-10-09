# GetDataLabelingJobResponseProgress


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**failed** | **int** | The number of objects that have failed to be labeled.  | [optional] 
**labeled** | **int** | The number of objects that have been labeled.  | [optional] 
**timeout** | **int** | The number of objects that have timed out to be labeled.            | [optional] 

## Example

```python
from zuora_sdk.models.get_data_labeling_job_response_progress import GetDataLabelingJobResponseProgress

# TODO update the JSON string below
json = "{}"
# create an instance of GetDataLabelingJobResponseProgress from a JSON string
get_data_labeling_job_response_progress_instance = GetDataLabelingJobResponseProgress.from_json(json)
# print the JSON string representation of the object
print(GetDataLabelingJobResponseProgress.to_json())

# convert the object into a dict
get_data_labeling_job_response_progress_dict = get_data_labeling_job_response_progress_instance.to_dict()
# create an instance of GetDataLabelingJobResponseProgress from a dict
get_data_labeling_job_response_progress_from_dict = GetDataLabelingJobResponseProgress.from_dict(get_data_labeling_job_response_progress_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


