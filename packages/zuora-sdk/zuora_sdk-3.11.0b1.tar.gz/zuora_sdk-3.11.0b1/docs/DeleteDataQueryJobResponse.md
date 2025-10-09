# DeleteDataQueryJobResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**DataQueryJobCancelled**](DataQueryJobCancelled.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.delete_data_query_job_response import DeleteDataQueryJobResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DeleteDataQueryJobResponse from a JSON string
delete_data_query_job_response_instance = DeleteDataQueryJobResponse.from_json(json)
# print the JSON string representation of the object
print(DeleteDataQueryJobResponse.to_json())

# convert the object into a dict
delete_data_query_job_response_dict = delete_data_query_job_response_instance.to_dict()
# create an instance of DeleteDataQueryJobResponse from a dict
delete_data_query_job_response_from_dict = DeleteDataQueryJobResponse.from_dict(delete_data_query_job_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


