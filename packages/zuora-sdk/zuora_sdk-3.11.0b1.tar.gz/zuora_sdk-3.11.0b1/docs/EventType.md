# EventType


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** | The description of the event type. | [optional] 
**display_name** | **str** | The display name for the event type. | 
**name** | **str** | The name of the event. Should be unique, contain no space, and be in the pattern: ^[A-Za-z]{1,}[\\\\w\\\\-]*$ | 

## Example

```python
from zuora_sdk.models.event_type import EventType

# TODO update the JSON string below
json = "{}"
# create an instance of EventType from a JSON string
event_type_instance = EventType.from_json(json)
# print the JSON string representation of the object
print(EventType.to_json())

# convert the object into a dict
event_type_dict = event_type_instance.to_dict()
# create an instance of EventType from a dict
event_type_from_dict = EventType.from_dict(event_type_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


