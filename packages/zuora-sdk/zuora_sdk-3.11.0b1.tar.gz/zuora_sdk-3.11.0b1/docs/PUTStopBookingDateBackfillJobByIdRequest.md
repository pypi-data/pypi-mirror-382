# PUTStopBookingDateBackfillJobByIdRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** | Stopping is only allowed value now | 

## Example

```python
from zuora_sdk.models.put_stop_booking_date_backfill_job_by_id_request import PUTStopBookingDateBackfillJobByIdRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PUTStopBookingDateBackfillJobByIdRequest from a JSON string
put_stop_booking_date_backfill_job_by_id_request_instance = PUTStopBookingDateBackfillJobByIdRequest.from_json(json)
# print the JSON string representation of the object
print(PUTStopBookingDateBackfillJobByIdRequest.to_json())

# convert the object into a dict
put_stop_booking_date_backfill_job_by_id_request_dict = put_stop_booking_date_backfill_job_by_id_request_instance.to_dict()
# create an instance of PUTStopBookingDateBackfillJobByIdRequest from a dict
put_stop_booking_date_backfill_job_by_id_request_from_dict = PUTStopBookingDateBackfillJobByIdRequest.from_dict(put_stop_booking_date_backfill_job_by_id_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


