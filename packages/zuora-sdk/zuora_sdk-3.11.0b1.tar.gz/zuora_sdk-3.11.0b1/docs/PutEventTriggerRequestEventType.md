# PutEventTriggerRequestEventType

The type of events to be triggered.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** | The description for the event type. | [optional] 
**display_name** | **str** | The display name for the event type. | [optional] 

## Example

```python
from zuora_sdk.models.put_event_trigger_request_event_type import PutEventTriggerRequestEventType

# TODO update the JSON string below
json = "{}"
# create an instance of PutEventTriggerRequestEventType from a JSON string
put_event_trigger_request_event_type_instance = PutEventTriggerRequestEventType.from_json(json)
# print the JSON string representation of the object
print(PutEventTriggerRequestEventType.to_json())

# convert the object into a dict
put_event_trigger_request_event_type_dict = put_event_trigger_request_event_type_instance.to_dict()
# create an instance of PutEventTriggerRequestEventType from a dict
put_event_trigger_request_event_type_from_dict = PutEventTriggerRequestEventType.from_dict(put_event_trigger_request_event_type_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


