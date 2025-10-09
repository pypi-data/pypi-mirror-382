# GetDataQueryJobsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**List[DataQueryJob]**](DataQueryJob.md) | List of data query jobs. The query jobs are listed in reverse order of creation. | [optional] 

## Example

```python
from zuora_sdk.models.get_data_query_jobs_response import GetDataQueryJobsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetDataQueryJobsResponse from a JSON string
get_data_query_jobs_response_instance = GetDataQueryJobsResponse.from_json(json)
# print the JSON string representation of the object
print(GetDataQueryJobsResponse.to_json())

# convert the object into a dict
get_data_query_jobs_response_dict = get_data_query_jobs_response_instance.to_dict()
# create an instance of GetDataQueryJobsResponse from a dict
get_data_query_jobs_response_from_dict = GetDataQueryJobsResponse.from_dict(get_data_query_jobs_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


