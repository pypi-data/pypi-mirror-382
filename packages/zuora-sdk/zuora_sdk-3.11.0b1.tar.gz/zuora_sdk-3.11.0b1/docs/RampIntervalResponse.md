# RampIntervalResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** | The short description of the interval. | [optional] 
**end_date** | **date** | The end date of the interval. | [optional] 
**name** | **str** | The name of the interval. | [optional] 
**start_date** | **date** | The start date of the interval. | [optional] 

## Example

```python
from zuora_sdk.models.ramp_interval_response import RampIntervalResponse

# TODO update the JSON string below
json = "{}"
# create an instance of RampIntervalResponse from a JSON string
ramp_interval_response_instance = RampIntervalResponse.from_json(json)
# print the JSON string representation of the object
print(RampIntervalResponse.to_json())

# convert the object into a dict
ramp_interval_response_dict = ramp_interval_response_instance.to_dict()
# create an instance of RampIntervalResponse from a dict
ramp_interval_response_from_dict = RampIntervalResponse.from_dict(ramp_interval_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


