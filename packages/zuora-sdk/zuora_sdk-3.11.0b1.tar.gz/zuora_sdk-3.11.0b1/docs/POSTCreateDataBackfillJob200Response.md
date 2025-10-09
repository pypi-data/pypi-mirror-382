# POSTCreateDataBackfillJob200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**job_id** | **str** | String of 32 characters that identifies the Data Backfill job.  The id is generated before the job is processed.  You can use the id to get the Data Backfill job result. | [optional] 

## Example

```python
from zuora_sdk.models.post_create_data_backfill_job200_response import POSTCreateDataBackfillJob200Response

# TODO update the JSON string below
json = "{}"
# create an instance of POSTCreateDataBackfillJob200Response from a JSON string
post_create_data_backfill_job200_response_instance = POSTCreateDataBackfillJob200Response.from_json(json)
# print the JSON string representation of the object
print(POSTCreateDataBackfillJob200Response.to_json())

# convert the object into a dict
post_create_data_backfill_job200_response_dict = post_create_data_backfill_job200_response_instance.to_dict()
# create an instance of POSTCreateDataBackfillJob200Response from a dict
post_create_data_backfill_job200_response_from_dict = POSTCreateDataBackfillJob200Response.from_dict(post_create_data_backfill_job200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


