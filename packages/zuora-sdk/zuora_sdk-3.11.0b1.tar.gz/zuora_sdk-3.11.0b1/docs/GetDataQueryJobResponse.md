# GetDataQueryJobResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**DataQueryJob**](DataQueryJob.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.get_data_query_job_response import GetDataQueryJobResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GetDataQueryJobResponse from a JSON string
get_data_query_job_response_instance = GetDataQueryJobResponse.from_json(json)
# print the JSON string representation of the object
print(GetDataQueryJobResponse.to_json())

# convert the object into a dict
get_data_query_job_response_dict = get_data_query_job_response_instance.to_dict()
# create an instance of GetDataQueryJobResponse from a dict
get_data_query_job_response_from_dict = GetDataQueryJobResponse.from_dict(get_data_query_job_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


