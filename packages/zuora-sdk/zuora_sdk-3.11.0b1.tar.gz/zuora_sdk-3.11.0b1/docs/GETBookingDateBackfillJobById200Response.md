# GETBookingDateBackfillJobById200Response


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process_id** | **str** | The Id of the process that handle the operation.  | [optional] 
**request_id** | **str** | Unique request identifier. If you need to contact us about a specific request, providing the request identifier will ensure the fastest possible resolution.  | [optional] 
**reasons** | [**List[FailedReason]**](FailedReason.md) |  | [optional] 
**success** | **bool** | Indicates whether the call succeeded.  | [optional] [default to True]
**job** | [**BookingDateJob**](BookingDateJob.md) |  | [optional] 

## Example

```python
from zuora_sdk.models.get_booking_date_backfill_job_by_id200_response import GETBookingDateBackfillJobById200Response

# TODO update the JSON string below
json = "{}"
# create an instance of GETBookingDateBackfillJobById200Response from a JSON string
get_booking_date_backfill_job_by_id200_response_instance = GETBookingDateBackfillJobById200Response.from_json(json)
# print the JSON string representation of the object
print(GETBookingDateBackfillJobById200Response.to_json())

# convert the object into a dict
get_booking_date_backfill_job_by_id200_response_dict = get_booking_date_backfill_job_by_id200_response_instance.to_dict()
# create an instance of GETBookingDateBackfillJobById200Response from a dict
get_booking_date_backfill_job_by_id200_response_from_dict = GETBookingDateBackfillJobById200Response.from_dict(get_booking_date_backfill_job_by_id200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


