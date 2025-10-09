# DataQueryJobCancelled

A cancelled data query job. 

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_by** | **str** | The query job creator&#39;s Id.  | [optional] 
**id** | **str** | Internal identifier of the query job.  | [optional] 
**query** | **str** | The query that was submitted.  | [optional] 
**source_data** | [**SubmitDataQueryRequestSourceData**](SubmitDataQueryRequestSourceData.md) |  | [optional] 
**remaining_retries** | **int** | The number of times that Zuora will retry the query if Zuora is unable to perform the query. | [optional] 
**updated_on** | **datetime** | Date and time when the query job was last updated, in ISO 8601 format.  | [optional] 
**use_index_join** | **bool** | Indicates whether to use Index Join.  | [optional] 
**query_status** | **str** | Status of the query job.  | [optional] 

## Example

```python
from zuora_sdk.models.data_query_job_cancelled import DataQueryJobCancelled

# TODO update the JSON string below
json = "{}"
# create an instance of DataQueryJobCancelled from a JSON string
data_query_job_cancelled_instance = DataQueryJobCancelled.from_json(json)
# print the JSON string representation of the object
print(DataQueryJobCancelled.to_json())

# convert the object into a dict
data_query_job_cancelled_dict = data_query_job_cancelled_instance.to_dict()
# create an instance of DataQueryJobCancelled from a dict
data_query_job_cancelled_from_dict = DataQueryJobCancelled.from_dict(data_query_job_cancelled_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


