# BookingDateJob


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Job id | [optional] 
**created_on** | **int** |  | [optional] 
**created_on_readable** | **str** |  | [optional] 
**updated_on** | **int** |  | [optional] 
**updated_on_readable** | **str** |  | [optional] 
**updated_by_username** | **str** |  | [optional] 
**status** | **str** | Data Backfill job type | [optional] 
**batch_sent_count** | **int** |  | [optional] 
**batch_finished_count** | **int** |  | [optional] 
**error_count** | **int** |  | [optional] 
**progress** | **str** |  | [optional] 

## Example

```python
from zuora_sdk.models.booking_date_job import BookingDateJob

# TODO update the JSON string below
json = "{}"
# create an instance of BookingDateJob from a JSON string
booking_date_job_instance = BookingDateJob.from_json(json)
# print the JSON string representation of the object
print(BookingDateJob.to_json())

# convert the object into a dict
booking_date_job_dict = booking_date_job_instance.to_dict()
# create an instance of BookingDateJob from a dict
booking_date_job_from_dict = BookingDateJob.from_dict(booking_date_job_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


