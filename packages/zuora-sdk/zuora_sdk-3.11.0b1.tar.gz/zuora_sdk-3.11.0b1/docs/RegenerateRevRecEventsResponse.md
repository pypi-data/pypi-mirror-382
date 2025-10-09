# RegenerateRevRecEventsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Indicates whether the call succeeded.  | [optional] 
**process_id** | **str** | The Id of the process that handles the operation.  | [optional] 

## Example

```python
from zuora_sdk.models.regenerate_rev_rec_events_response import RegenerateRevRecEventsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of RegenerateRevRecEventsResponse from a JSON string
regenerate_rev_rec_events_response_instance = RegenerateRevRecEventsResponse.from_json(json)
# print the JSON string representation of the object
print(RegenerateRevRecEventsResponse.to_json())

# convert the object into a dict
regenerate_rev_rec_events_response_dict = regenerate_rev_rec_events_response_instance.to_dict()
# create an instance of RegenerateRevRecEventsResponse from a dict
regenerate_rev_rec_events_response_from_dict = RegenerateRevRecEventsResponse.from_dict(regenerate_rev_rec_events_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


