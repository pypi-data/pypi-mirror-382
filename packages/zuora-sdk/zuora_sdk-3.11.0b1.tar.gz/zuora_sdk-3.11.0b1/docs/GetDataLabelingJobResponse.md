# GetDataLabelingJobResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job_id** | **str** | Identifier of the data labeling job.  | [optional] 
**job_status** | **str** | Status of the data labeling job.   * &#x60;Accepted&#x60; - The data labeling job has been accepted by the system.  * &#x60;Dispatched&#x60; - The data labeling job is dispatched to the data labeling service.  * &#x60;Completed&#x60; - The data labeling job has completed. Please note that &#x60;Completed&#x60; simply means the data labeling job has completed, but it does not mean the data labeling job has labeled all the data. You can check the &#x60;progress&#x60; field to see how many data have been &#x60;labeled&#x60;, &#x60;failed&#x60; or &#x60;timeout&#x60;. | [optional] 
**object_type** | **str** | The object type of the data labeling job.  | [optional] 
**progress** | [**GetDataLabelingJobResponseProgress**](GetDataLabelingJobResponseProgress.md) |  | [optional] 
**success** | **bool** | Indicates whether the job was submitted successfully.  | [optional] 
**total_object** | **int** | The total number of objects to be labeled.  | [optional] 

## Example

```python
from zuora_sdk.models.get_data_labeling_job_response import GetDataLabelingJobResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetDataLabelingJobResponse from a JSON string
get_data_labeling_job_response_instance = GetDataLabelingJobResponse.from_json(json)
# print the JSON string representation of the object
print(GetDataLabelingJobResponse.to_json())

# convert the object into a dict
get_data_labeling_job_response_dict = get_data_labeling_job_response_instance.to_dict()
# create an instance of GetDataLabelingJobResponse from a dict
get_data_labeling_job_response_from_dict = GetDataLabelingJobResponse.from_dict(get_data_labeling_job_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


