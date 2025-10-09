# RampIntervalRequest

Container for the intervals that the ramp is split into in its timeline. Zuora can report metrics for this specific period.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** | The short description of the interval. | [optional] 
**end_date** | **date** | The end date of the interval. | 
**name** | **str** | The name of the interval. | [optional] 
**start_date** | **date** | The start date of the interval. | 

## Example

```python
from zuora_sdk.models.ramp_interval_request import RampIntervalRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RampIntervalRequest from a JSON string
ramp_interval_request_instance = RampIntervalRequest.from_json(json)
# print the JSON string representation of the object
print(RampIntervalRequest.to_json())

# convert the object into a dict
ramp_interval_request_dict = ramp_interval_request_instance.to_dict()
# create an instance of RampIntervalRequest from a dict
ramp_interval_request_from_dict = RampIntervalRequest.from_dict(ramp_interval_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


