# GETListDataBackfillJobs200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**jobs** | [**List[Job]**](Job.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.get_list_data_backfill_jobs200_response import GETListDataBackfillJobs200Response

# TODO update the JSON string below
json = "{}"
# create an instance of GETListDataBackfillJobs200Response from a JSON string
get_list_data_backfill_jobs200_response_instance = GETListDataBackfillJobs200Response.from_json(json)
# print the JSON string representation of the object
print(GETListDataBackfillJobs200Response.to_json())

# convert the object into a dict
get_list_data_backfill_jobs200_response_dict = get_list_data_backfill_jobs200_response_instance.to_dict()
# create an instance of GETListDataBackfillJobs200Response from a dict
get_list_data_backfill_jobs200_response_from_dict = GETListDataBackfillJobs200Response.from_dict(get_list_data_backfill_jobs200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


